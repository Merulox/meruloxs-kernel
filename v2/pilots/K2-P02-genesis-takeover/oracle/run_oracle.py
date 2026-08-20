#!/usr/bin/env python3
"""Verifier-owned behavioral oracle for the K2-P02 public contract."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib
import inspect
import io
import json
import os
from pathlib import Path
import sqlite3
import stat
import sys
import tempfile
import threading
from typing import Any, Callable, Iterable


class ContractFailure(Exception):
    def __init__(self, invariant: str, counterexample: str) -> None:
        super().__init__(counterexample)
        self.invariant = invariant
        self.counterexample = counterexample


class ContainmentViolation(Exception):
    pass


class ExpectedRefusal(Exception):
    pass


_RUNTIME: Any = None
_BROKER_CLASS: Any = None
_STORE_CLASS: Any = None
_ROOT: Path | None = None
_REPO: Path | None = None


_REQUEST_STATES = {
    "proposed",
    "approved",
    "executing",
    "succeeded",
    "failed",
    "rejected",
    "expired",
    "cancelled",
    "rolling_back",
    "rolled_back",
    "rollback_failed",
}


def _fail(invariant: str, message: str) -> None:
    raise ContractFailure(invariant, message)


def _assert(condition: bool, invariant: str, message: str) -> None:
    if not condition:
        _fail(invariant, message)


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root)
        return True
    except ValueError:
        return False


def _install_containment(root: Path) -> None:
    write_mask = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND

    def checked_path(raw: Any, event: str) -> None:
        if isinstance(raw, int) or raw is None:
            return
        try:
            path = Path(os.fsdecode(raw))
        except (TypeError, ValueError):
            raise ContainmentViolation(f"unsupported path in {event}")
        if not path.is_absolute():
            path = Path.cwd() / path
        if not _inside(path, root):
            raise ContainmentViolation(f"write boundary escaped disposable root during {event}")

    def hook(event: str, args: tuple[Any, ...]) -> None:
        if event == "open" and args:
            mode = args[1] if len(args) > 1 else "r"
            flags = args[2] if len(args) > 2 else 0
            writing = (
                isinstance(mode, str)
                and any(marker in mode for marker in ("w", "a", "x", "+"))
            ) or (isinstance(flags, int) and bool(flags & write_mask))
            if writing:
                checked_path(args[0], event)
            return
        if event in {
            "os.remove",
            "os.rmdir",
            "os.mkdir",
            "os.chmod",
            "os.truncate",
            "os.utime",
            "os.symlink",
            "os.link",
        } and args:
            checked_path(args[0], event)
            if event in {"os.symlink", "os.link"} and len(args) > 1:
                checked_path(args[1], event)
            return
        if event in {"os.rename", "os.replace"} and len(args) >= 2:
            checked_path(args[0], event)
            checked_path(args[1], event)
            return
        if event.startswith("socket.") and event not in {"socket.__new__"}:
            raise ContainmentViolation("network access is forbidden")
        if event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.posix_spawnp"}:
            raise ContainmentViolation("process execution is forbidden")

    sys.addaudithook(hook)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _walk(value: Any) -> Iterable[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk(child)


def _contains(value: Any, expected: Any) -> bool:
    return any(item == expected for item in _walk(value))


def _request_record(view: dict[str, Any]) -> dict[str, Any]:
    request = view.get("request")
    if isinstance(request, dict):
        return request
    return view


def _request_state(view: dict[str, Any]) -> str | None:
    record = _request_record(view)
    for key in ("state", "request_state", "status"):
        value = record.get(key)
        if isinstance(value, str) and value in _REQUEST_STATES:
            return value
    for item in _walk(record):
        if isinstance(item, dict):
            value = item.get("state")
            if isinstance(value, str) and value in _REQUEST_STATES:
                return value
    return None


def _attempt_records(view: dict[str, Any]) -> list[dict[str, Any]]:
    for item in _walk(view):
        if isinstance(item, dict):
            attempts = item.get("attempts")
            if isinstance(attempts, list) and all(isinstance(row, dict) for row in attempts):
                return attempts
    return []


def _attempt_number(claim: Any) -> int:
    if isinstance(claim, dict):
        value = claim.get("attempt")
    else:
        value = getattr(claim, "attempt", None)
    if not isinstance(value, int):
        _fail("P02-I8", "execution claim did not expose a positive attempt number")
    return value


def _claim_digest(claim: Any) -> str | None:
    if isinstance(claim, dict):
        value = claim.get("request_digest")
    else:
        value = getattr(claim, "request_digest", None)
    return value if isinstance(value, str) else None


def _looks_refused(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    for key in ("ok", "success", "accepted"):
        if result.get(key) is False:
            return True
    for key in ("status", "state", "result", "verdict"):
        value = result.get(key)
        if isinstance(value, str) and value.lower() in {
            "error",
            "failed",
            "refused",
            "rejected",
            "denied",
            "not_found",
            "conflict",
        }:
            return True
    return False


def _expect_refusal(call: Callable[[], Any], invariant: str, message: str) -> None:
    try:
        result = call()
    except (ContractFailure, ContainmentViolation):
        raise
    except Exception:
        return
    if not _looks_refused(result):
        _fail(invariant, message)


def _takeover_id(value: dict[str, Any]) -> str | None:
    for key in ("takeover_id", "id"):
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate:
            return candidate
    for key in ("takeover", "active_takeover", "active"):
        child = value.get(key)
        if isinstance(child, dict):
            candidate = _takeover_id(child)
            if candidate:
                return candidate
    for item in _walk(value):
        if isinstance(item, dict) and item is not value:
            candidate = item.get("takeover_id")
            if isinstance(candidate, str) and candidate:
                return candidate
    return None


def _active_takeover_id(view: dict[str, Any]) -> str | None:
    active = view.get("active_takeover")
    if active is None and "active" in view:
        active = view.get("active")
    if isinstance(active, dict):
        return _takeover_id(active)
    if active is True:
        return _takeover_id(view)
    if active in (False, None):
        takeover = view.get("takeover")
        if isinstance(takeover, dict) and takeover.get("active") is True:
            return _takeover_id(takeover)
        return None
    return None


def _now(offset_seconds: int = 0) -> int:
    return 2_051_222_400 + offset_seconds


def _sha(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _locate_runtime(repo: Path) -> None:
    global _RUNTIME, _BROKER_CLASS, _STORE_CLASS
    sys.dont_write_bytecode = True
    for name in list(sys.modules):
        if name == "runtime_v2" or name.startswith("runtime_v2."):
            del sys.modules[name]
    sys.path.insert(0, str(repo))
    try:
        runtime = importlib.import_module("runtime_v2")
    except Exception as exc:
        _fail("P02-I8", f"public runtime_v2 import failed: {type(exc).__name__}")
    origin_raw = getattr(runtime, "__file__", None)
    if not origin_raw:
        _fail("P02-I8", "public runtime_v2 import had no repository origin")
    origin = Path(origin_raw).resolve()
    if not _inside(origin, repo):
        _fail("P02-I10", "runtime_v2 resolved outside the supplied candidate repository")

    broker = getattr(runtime, "CapabilityBroker", None)
    modules = [runtime]
    for suffix in ("capabilities", "store", "storage", "db"):
        try:
            module = importlib.import_module(f"runtime_v2.{suffix}")
        except ModuleNotFoundError as exc:
            if exc.name == f"runtime_v2.{suffix}":
                continue
            _fail("P02-I8", f"public runtime dependency import failed: {type(exc).__name__}")
        except Exception as exc:
            _fail("P02-I8", f"public runtime import failed: {type(exc).__name__}")
        modules.append(module)
        if broker is None:
            broker = getattr(module, "CapabilityBroker", None)
    if not inspect.isclass(broker):
        _fail("P02-I8", "runtime_v2 did not expose CapabilityBroker")

    candidates = (
        "RuntimeStore",
        "SQLiteStateStore",
        "SQLiteStore",
        "CapabilityStore",
        "StateStore",
    )
    store = None
    for module in modules:
        for name in candidates:
            candidate = getattr(module, name, None)
            if inspect.isclass(candidate):
                store = candidate
                break
        if store is not None:
            break
    if store is None:
        try:
            annotation = inspect.signature(broker).parameters["store"].annotation
            if inspect.isclass(annotation):
                store = annotation
        except (KeyError, TypeError, ValueError):
            pass
    if store is None:
        _fail("P02-I8", "runtime_v2 did not expose its documented SQLite store dependency")

    _RUNTIME = runtime
    _BROKER_CLASS = broker
    _STORE_CLASS = store


def _new_store(db_path: Path) -> Any:
    attempts: list[Callable[[], Any]] = [
        lambda: _STORE_CLASS(db_path),
        lambda: _STORE_CLASS(str(db_path)),
        lambda: _STORE_CLASS(path=db_path),
        lambda: _STORE_CLASS(db_path=db_path),
        lambda: _STORE_CLASS(database_path=db_path),
    ]
    last: Exception | None = None
    for construct in attempts:
        try:
            return construct()
        except TypeError as exc:
            last = exc
    _fail("P02-I8", f"documented broker store could not be constructed: {type(last).__name__}")


def _new_broker(case: str, *, initialize: bool = True) -> tuple[Any, Any, Path, Path]:
    assert _ROOT is not None
    base = _ROOT / case
    base.mkdir(mode=0o700)
    db_path = base / "capability.sqlite3"
    workspace = base / "workspace"
    store = _new_store(db_path)
    try:
        broker = _BROKER_CLASS(
            store,
            workspace,
            allowed_approvers={"merulox"},
            approval_ttl_seconds=3600,
        )
    except TypeError:
        broker = _BROKER_CLASS(store, workspace, {"merulox"}, 3600)
    for method in (
        "initialize",
        "propose",
        "approve",
        "claim",
        "execute_claim",
        "recover_expired",
        "rollback",
        "inspect",
        "status",
        "cancel",
        "takeover",
        "release_takeover",
        "inspect_takeover",
    ):
        if not callable(getattr(broker, method, None)):
            _fail("P02-I8", f"broker is missing required public method {method}")
    if initialize:
        store_initialize = getattr(store, "initialize", None)
        if callable(store_initialize):
            store_initialize()
        broker.initialize()
    return broker, store, db_path, workspace


def _close_store(store: Any) -> None:
    close = getattr(store, "close", None)
    if callable(close):
        close()

def _with_peer(db_path: Path, workspace: Path, call: Callable[[Any], Any]) -> Any:
    store = _new_store(db_path)
    try:
        store_initialize = getattr(store, "initialize", None)
        if callable(store_initialize):
            store_initialize()
        try:
            broker = _BROKER_CLASS(
                store,
                workspace,
                allowed_approvers={"merulox"},
                approval_ttl_seconds=3600,
            )
        except TypeError:
            broker = _BROKER_CLASS(store, workspace, {"merulox"}, 3600)
        broker.initialize()
        return call(broker)
    finally:
        _close_store(store)


def _propose(
    broker: Any,
    key: str,
    filename: str,
    content: str,
    *,
    expected: str = "absent",
    at: int | None = None,
) -> tuple[str, str]:
    current = at or _now()
    result = broker.propose(
        key,
        "workspace.write_text",
        {"filename": filename, "content": content, "expected_sha256": expected},
        "oracle-requester",
        {"source": "protected-oracle", "case": key},
        current + 7200,
        now=current,
    )
    if not isinstance(result, (tuple, list)) or len(result) != 3:
        _fail("P02-I8", "proposal did not return request ID, creation flag, and digest")
    request_id, created, digest = result
    if not isinstance(request_id, str) or not request_id:
        _fail("P02-I8", "proposal returned an invalid request ID")
    if not isinstance(created, bool) or not isinstance(digest, str) or len(digest) != 64:
        _fail("P02-I8", "proposal returned invalid immutable identity evidence")
    return request_id, digest


def _approve(broker: Any, request_id: str, digest: str, *, at: int | None = None) -> Any:
    return broker.approve(
        request_id,
        digest,
        "merulox",
        "oracle approval",
        now=at or _now(),
    )


def _state(broker: Any, request_id: str, invariant: str) -> tuple[str, dict[str, Any]]:
    view = broker.inspect(request_id)
    if not isinstance(view, dict):
        _fail(invariant, "request inspection did not return a dictionary")
    state = _request_state(view)
    if state is None:
        _fail(invariant, "request inspection did not expose its durable state")
    return state, view


def _file_snapshot(path: Path) -> tuple[bool, bytes | None, int | None]:
    if not path.exists() and not path.is_symlink():
        return False, None, None
    if path.is_symlink():
        return True, os.readlink(path).encode(), None
    data = path.read_bytes() if path.is_file() else None
    mode = stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)
    return True, data, mode


def _cancel_refusal_keeps_state(
    broker: Any,
    request_id: str,
    call: Callable[[], Any],
    invariant: str,
    message: str,
    target: Path | None = None,
) -> None:
    before_state, before_view = _state(broker, request_id, invariant)
    before_file = _file_snapshot(target) if target is not None else None
    _expect_refusal(call, invariant, message)
    after_state, after_view = _state(broker, request_id, invariant)
    _assert(after_state == before_state, invariant, message)
    if target is not None:
        _assert(_file_snapshot(target) == before_file, invariant, message)
    _assert(
        _canonical(after_view) != _canonical(before_view),
        invariant,
        "a cancellation refusal was not durably inspectable",
    )


def _case_a() -> None:
    invariant = "P02-I1"
    broker, _, _, workspace = _new_broker("a")
    request_id, digest = _propose(broker, "a-main", "authority.txt", "never")
    target = workspace / "authority.txt"

    _cancel_refusal_keeps_state(
        broker,
        request_id,
        lambda: broker.cancel(request_id, "0" * 64, "merulox", "wrong digest", now=_now(1)),
        invariant,
        "wrong digest cancellation changed the request",
        target,
    )
    _cancel_refusal_keeps_state(
        broker,
        request_id,
        lambda: broker.cancel(request_id, digest, "intruder", "unauthorized", now=_now(2)),
        invariant,
        "unauthorized cancellation changed the request",
        target,
    )
    _cancel_refusal_keeps_state(
        broker,
        request_id,
        lambda: broker.cancel(request_id, digest, "merulox", "", now=_now(3)),
        invariant,
        "empty-reason cancellation changed the request",
        target,
    )
    _cancel_refusal_keeps_state(
        broker,
        request_id,
        lambda: broker.cancel(request_id, digest, "merulox", "x" * 100_000, now=_now(4)),
        invariant,
        "unbounded cancellation reason was accepted",
        target,
    )
    _expect_refusal(
        lambda: broker.cancel("unknown-request", digest, "merulox", "unknown", now=_now(5)),
        invariant,
        "unknown request cancellation was accepted",
    )

    result = broker.cancel(request_id, digest, "merulox", "valid cancellation", now=_now(6))
    _assert(isinstance(result, dict) and not _looks_refused(result), invariant, "valid cancellation was refused")
    state, view = _state(broker, request_id, invariant)
    _assert(state == "cancelled", invariant, "valid proposed request did not become cancelled")
    _assert(not target.exists(), invariant, "valid pre-effect cancellation produced a file effect")
    for evidence in (digest, "merulox", "valid cancellation"):
        _assert(_contains(view, evidence), invariant, "cancellation evidence was incomplete")
    _cancel_refusal_keeps_state(
        broker,
        request_id,
        lambda: broker.cancel(request_id, digest, "merulox", "duplicate", now=_now(7)),
        invariant,
        "duplicate cancellation changed terminal cancelled state",
        target,
    )

    terminal_id, terminal_digest = _propose(broker, "a-terminal", "terminal.txt", "done", at=_now(8))
    _approve(broker, terminal_id, terminal_digest, at=_now(8))
    terminal_claim = broker.claim("terminal-worker", now=_now(9))
    broker.execute_claim(terminal_claim, now=_now(10))
    _cancel_refusal_keeps_state(
        broker,
        terminal_id,
        lambda: broker.cancel(terminal_id, terminal_digest, "merulox", "too late", now=_now(11)),
        invariant,
        "terminal succeeded request was cancelled",
        workspace / "terminal.txt",
    )


def _case_b() -> None:
    invariant = "P02-I2"
    broker, _, _, workspace = _new_broker("b")

    proposed_id, proposed_digest = _propose(broker, "b-p", "proposed.txt", "p")
    broker.cancel(proposed_id, proposed_digest, "merulox", "cancel proposed", now=_now(1))
    _assert(_state(broker, proposed_id, invariant)[0] == "cancelled", invariant, "proposed request was not cancellable")

    approved_id, approved_digest = _propose(broker, "b-a", "approved.txt", "a")
    _approve(broker, approved_id, approved_digest)
    broker.cancel(approved_id, approved_digest, "merulox", "cancel approved", now=_now(2))
    _assert(_state(broker, approved_id, invariant)[0] == "cancelled", invariant, "approved request was not cancellable")

    executing_id, executing_digest = _propose(broker, "b-e", "executing.txt", "e")
    _approve(broker, executing_id, executing_digest)
    claim = broker.claim("worker-b", lease_seconds=30, now=_now(3))
    _assert(claim is not None, invariant, "approved request could not be claimed")
    broker.cancel(executing_id, executing_digest, "merulox", "cancel executing", now=_now(4))
    state, view = _state(broker, executing_id, invariant)
    _assert(state == "cancelled", invariant, "not-yet-applied executing request was not cancelled")
    attempts = _attempt_records(view)
    _assert(
        any(row.get("state", row.get("status")) == "cancelled" for row in attempts),
        invariant,
        "active execution attempt was not durably terminalized as cancelled",
    )
    _expect_refusal(
        lambda: broker.execute_claim(claim, now=_now(5)),
        invariant,
        "cancelled claim remained usable by its worker",
    )
    _assert(not (workspace / "executing.txt").exists(), invariant, "cancelled stale claim produced a file effect")
    _assert(broker.claim("worker-after-cancel", now=_now(6)) is None, invariant, "cancelled request remained claimable")


def _threaded_pair(left: Callable[[], Any], right: Callable[[], Any]) -> list[tuple[bool, Any]]:
    barrier = threading.Barrier(3)
    results: list[tuple[bool, Any] | None] = [None, None]

    def run(index: int, call: Callable[[], Any]) -> None:
        barrier.wait()
        try:
            value = call()
            results[index] = (not _looks_refused(value), value)
        except Exception as exc:
            results[index] = (False, exc)

    threads = [threading.Thread(target=run, args=(0, left)), threading.Thread(target=run, args=(1, right))]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=10)
    if any(thread.is_alive() for thread in threads):
        raise RuntimeError("concurrent public operation did not terminate")
    return [item for item in results if item is not None]


def _case_c() -> None:
    invariant = "P02-I3"
    broker, _, db_path, workspace = _new_broker("c")

    same_id, same_digest = _propose(broker, "c-same", "same.txt", "same")
    same_results = _threaded_pair(
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.cancel(same_id, same_digest, "merulox", "left cancellation", now=_now(1)),
        ),
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.cancel(same_id, same_digest, "merulox", "right cancellation", now=_now(1)),
        ),
    )
    _assert(len(same_results) == 2, invariant, "concurrent cancellation lost an outcome")
    _assert(sum(1 for ok, _ in same_results if ok) == 1, invariant, "concurrent cancellation did not produce exactly one winner")
    _assert(_state(broker, same_id, invariant)[0] == "cancelled", invariant, "single-winner cancellation did not terminalize request")

    for index in range(8):
        filename = f"race-{index}.txt"
        request_id, digest = _propose(broker, f"c-race-{index}", filename, f"value-{index}")
        _approve(broker, request_id, digest, at=_now(10 + index))
        claim = broker.claim(f"race-worker-{index}", lease_seconds=30, now=_now(20 + index))
        _assert(claim is not None, invariant, "race request could not reach executing state")
        outcomes = _threaded_pair(
            lambda rid=request_id, dig=digest, n=index: _with_peer(
                db_path,
                workspace,
                lambda peer: peer.cancel(rid, dig, "merulox", f"race cancel {n}", now=_now(30 + n)),
            ),
            lambda c=claim, n=index: _with_peer(
                db_path,
                workspace,
                lambda peer: peer.execute_claim(c, now=_now(30 + n)),
            ),
        )
        _assert(len(outcomes) == 2, invariant, "cancellation/execution race lost an outcome")
        _assert(sum(1 for ok, _ in outcomes if ok) == 1, invariant, "cancellation and execution both won or both failed")
        state, _ = _state(broker, request_id, invariant)
        target = workspace / filename
        if state == "cancelled":
            _assert(not target.exists(), invariant, "race reported cancelled after a filesystem effect")
        elif state == "succeeded":
            _assert(target.read_text() == f"value-{index}", invariant, "race reported succeeded without exact effect")
        else:
            _fail(invariant, f"race ended in unsupported state {state}")


def _prepare_takeover_set(case: str) -> tuple[Any, Path, Path, str, list[tuple[str, str]], Any]:
    broker, _, db_path, workspace = _new_broker(case)
    filename = "shared.txt"
    existing_id, existing_digest = _propose(broker, f"{case}-existing", filename, "stable")
    _approve(broker, existing_id, existing_digest)
    existing_claim = broker.claim(f"{case}-existing-worker", now=_now(1))
    broker.execute_claim(existing_claim, now=_now(2))
    expected = _sha("stable")

    proposed = _propose(broker, f"{case}-proposed", filename, "next-p", expected=expected, at=_now(3))
    executing = _propose(broker, f"{case}-executing", filename, "next-e", expected=expected, at=_now(4))
    _approve(broker, *executing, at=_now(4))
    executing_claim = broker.claim(f"{case}-worker", lease_seconds=30, now=_now(5))
    approved = _propose(broker, f"{case}-approved", filename, "next-a", expected=expected, at=_now(6))
    _approve(broker, *approved, at=_now(6))
    return broker, db_path, workspace, filename, [proposed, executing, approved], executing_claim


def _case_d() -> None:
    invariant = "P02-I4"
    broker, db_path, workspace, filename, requests, _ = _prepare_takeover_set("d")
    target = workspace / filename
    before = _file_snapshot(target)
    result = broker.takeover(filename, "merulox", "human control", now=_now(10))
    _assert(isinstance(result, dict) and not _looks_refused(result), invariant, "valid takeover was refused")
    takeover_id = _takeover_id(result)
    _assert(bool(takeover_id), invariant, "takeover did not return an exact takeover ID")
    _assert(_file_snapshot(target) == before, invariant, "takeover changed an existing verified effect")
    for request_id, _ in requests:
        _assert(_state(broker, request_id, invariant)[0] == "cancelled", invariant, "takeover did not cancel every outstanding filename request")
    view = broker.inspect_takeover(filename)
    _assert(isinstance(view, dict), invariant, "takeover inspection was not a dictionary")
    _assert(_active_takeover_id(view) == takeover_id, invariant, "takeover was not durably active before return")

    for bad_filename in ("../escape", "/tmp/escape", "nested/name", ".", "..", "x" * 129):
        _expect_refusal(
            lambda name=bad_filename: broker.takeover(name, "merulox", "bad filename", now=_now(11)),
            invariant,
            "invalid takeover filename was accepted",
        )
    _expect_refusal(
        lambda: broker.takeover(filename, "intruder", "unauthorized", now=_now(12)),
        invariant,
        "unauthorized takeover was accepted",
    )
    _expect_refusal(
        lambda: broker.takeover(filename, "merulox", "", now=_now(13)),
        invariant,
        "empty-reason takeover was accepted",
    )
    _expect_refusal(
        lambda: broker.takeover(filename, "merulox", "x" * 100_000, now=_now(14)),
        invariant,
        "unbounded takeover reason was accepted",
    )

    concurrent = _threaded_pair(
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.takeover("concurrent.txt", "merulox", "left takeover", now=_now(15)),
        ),
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.takeover("concurrent.txt", "merulox", "right takeover", now=_now(15)),
        ),
    )
    _assert(
        sum(1 for ok, _ in concurrent if ok) == 1,
        invariant,
        "concurrent takeover did not produce exactly one active winner",
    )
    winning_ids = [
        _takeover_id(value)
        for ok, value in concurrent
        if ok and isinstance(value, dict)
    ]
    _assert(
        len(winning_ids) == 1
        and _active_takeover_id(broker.inspect_takeover("concurrent.txt")) == winning_ids[0],
        invariant,
        "concurrent takeover winner was not the single durable active record",
    )


def _case_e() -> None:
    invariant = "P02-I5"
    broker, _, workspace, filename, requests, stale_claim = _prepare_takeover_set("e")
    target = workspace / filename
    result = broker.takeover(filename, "merulox", "manual ownership", now=_now(10))
    _assert(_takeover_id(result) is not None, invariant, "takeover did not establish active fencing")
    stable = _file_snapshot(target)

    _expect_refusal(
        lambda: _propose(broker, "e-blocked-new", filename, "blocked", expected=_sha("stable"), at=_now(11)),
        invariant,
        "new proposal was accepted while filename was taken over",
    )
    cancelled_id, cancelled_digest = requests[0]
    _expect_refusal(
        lambda: broker.approve(cancelled_id, cancelled_digest, "merulox", "late approval", now=_now(12)),
        invariant,
        "approval boundary reopened work while filename was taken over",
    )
    _assert(broker.claim("taken-over-worker", now=_now(13)) is None, invariant, "taken-over request remained claimable")
    _expect_refusal(
        lambda: broker.execute_claim(stale_claim, now=_now(14)),
        invariant,
        "claim obtained before takeover executed afterward",
    )
    _assert(_file_snapshot(target) == stable, invariant, "a taken-over boundary mutated the target")


def _case_f() -> None:
    invariant = "P02-I6"
    broker, _, db_path, workspace = _new_broker("f")
    filename = "release.txt"
    first = broker.takeover(filename, "merulox", "first takeover", now=_now(1))
    first_id = _takeover_id(first)
    _assert(first_id is not None, invariant, "takeover did not provide release authority ID")

    for call, message in (
        (lambda: broker.release_takeover(filename, "wrong-id", "merulox", "wrong", now=_now(2)), "wrong takeover ID released active takeover"),
        (lambda: broker.release_takeover(filename, first_id, "intruder", "unauthorized", now=_now(3)), "unauthorized operator released takeover"),
        (lambda: broker.release_takeover(filename, first_id, "merulox", "", now=_now(4)), "empty-reason release was accepted"),
        (lambda: broker.release_takeover(filename, first_id, "merulox", "x" * 100_000, now=_now(5)), "unbounded release reason was accepted"),
        (lambda: broker.release_takeover("unknown.txt", first_id, "merulox", "unknown", now=_now(6)), "unknown filename release was accepted"),
    ):
        _expect_refusal(call, invariant, message)
        view = broker.inspect_takeover(filename)
        _assert(_active_takeover_id(view) == first_id, invariant, message)

    releases = _threaded_pair(
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.release_takeover(filename, first_id, "merulox", "left release", now=_now(7)),
        ),
        lambda: _with_peer(
            db_path,
            workspace,
            lambda peer: peer.release_takeover(filename, first_id, "merulox", "right release", now=_now(7)),
        ),
    )
    _assert(
        sum(1 for ok, _ in releases if ok) == 1,
        invariant,
        "concurrent exact releases did not produce one winner",
    )
    _assert(_active_takeover_id(broker.inspect_takeover(filename)) is None, invariant, "exact release left takeover active")
    _expect_refusal(
        lambda: broker.release_takeover(filename, first_id, "merulox", "duplicate", now=_now(8)),
        invariant,
        "duplicate release was accepted",
    )

    old_request, old_digest = _propose(broker, "f-old", filename, "old", at=_now(9))
    broker.cancel(old_request, old_digest, "merulox", "terminal before retake", now=_now(10))
    second = broker.takeover(filename, "merulox", "second takeover", now=_now(11))
    second_id = _takeover_id(second)
    _assert(second_id is not None and second_id != first_id, invariant, "new takeover reused a stale authority ID")
    _expect_refusal(
        lambda: broker.release_takeover(filename, first_id, "merulox", "stale release", now=_now(12)),
        invariant,
        "stale takeover ID released a newer takeover",
    )
    _assert(_active_takeover_id(broker.inspect_takeover(filename)) == second_id, invariant, "stale release mutated newer takeover")
    broker.release_takeover(filename, second_id, "merulox", "second release", now=_now(13))
    _assert(_state(broker, old_request, invariant)[0] == "cancelled", invariant, "release revived an earlier cancelled request")
    fresh_id, fresh_digest = _propose(broker, "f-fresh", filename, "fresh", at=_now(14))
    _approve(broker, fresh_id, fresh_digest, at=_now(14))
    claim = broker.claim("post-release-worker", now=_now(15))
    broker.execute_claim(claim, now=_now(16))
    _assert((workspace / filename).read_text() == "fresh", invariant, "release did not permit fresh automatic work")


def _case_g() -> None:
    invariant = "P02-I7"
    broker, _, _, _ = _new_broker("g")
    request_id, digest = _propose(broker, "g-cancel", "durable.txt", "never")
    broker.cancel(request_id, digest, "merulox", "durable cancellation", now=_now(1))
    first = broker.inspect(request_id)
    second = broker.inspect(request_id)
    _assert(_canonical(first) == _canonical(second), invariant, "request inspection ordering was nondeterministic")
    _assert(_request_state(first) == "cancelled", invariant, "inspection omitted cancelled request state")
    for evidence in (digest, "merulox", "durable cancellation"):
        _assert(_contains(first, evidence), invariant, "inspection omitted cancellation evidence")

    takeover = broker.takeover("durable.txt", "merulox", "durable takeover", now=_now(2))
    takeover_id = _takeover_id(takeover)
    broker.release_takeover("durable.txt", takeover_id, "merulox", "durable release", now=_now(3))
    history_a = broker.inspect_takeover("durable.txt")
    history_b = broker.inspect_takeover("durable.txt")
    _assert(_canonical(history_a) == _canonical(history_b), invariant, "takeover history ordering was nondeterministic")
    _assert(_active_takeover_id(history_a) is None, invariant, "released takeover remained active in inspection")
    for evidence in (takeover_id, "durable takeover", "durable release", "merulox"):
        _assert(_contains(history_a, evidence), invariant, "takeover inspection omitted append-only history evidence")


def _mutate_schema_marker_to_v2(db_path: Path) -> bool:
    changed = False
    connection = sqlite3.connect(db_path)
    try:
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        if user_version:
            connection.execute("PRAGMA user_version = 2")
            changed = True
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        ]
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            columns = [row[1] for row in connection.execute(f"PRAGMA table_info({quoted})")]
            lowered = {column.lower(): column for column in columns}
            for logical in ("schema_version", "version"):
                column = lowered.get(logical)
                if column and ("schema" in table.lower() or logical == "schema_version"):
                    qcol = '"' + column.replace('"', '""') + '"'
                    cursor = connection.execute(f"UPDATE {quoted} SET {qcol}=2 WHERE CAST({qcol} AS TEXT)='3'")
                    changed = changed or cursor.rowcount > 0
            key_column = next((lowered[name] for name in ("key", "name") if name in lowered), None)
            value_column = next((lowered[name] for name in ("value", "metadata_value") if name in lowered), None)
            if key_column and value_column:
                qkey = '"' + key_column.replace('"', '""') + '"'
                qvalue = '"' + value_column.replace('"', '""') + '"'
                cursor = connection.execute(
                    f"UPDATE {quoted} SET {qvalue}='2' WHERE lower(CAST({qkey} AS TEXT)) LIKE '%schema%version%' AND CAST({qvalue} AS TEXT)='3'"
                )
                changed = changed or cursor.rowcount > 0
        connection.commit()
    finally:
        connection.close()
    return changed


def _case_h() -> None:
    invariant = "P02-I8"
    broker, store, db_path, workspace = _new_broker("h")

    request_id, digest = _propose(broker, "h-dedupe", "baseline.txt", "baseline")
    repeated = broker.propose(
        "h-dedupe",
        "workspace.write_text",
        {"filename": "baseline.txt", "content": "baseline", "expected_sha256": "absent"},
        "oracle-requester",
        {"source": "protected-oracle", "case": "h-dedupe"},
        _now() + 7200,
        now=_now(),
    )
    _assert(repeated[0] == request_id and repeated[1] is False and repeated[2] == digest, invariant, "idempotent proposal did not preserve immutable identity")
    _expect_refusal(
        lambda: broker.propose(
            "h-dedupe",
            "workspace.write_text",
            {"filename": "baseline.txt", "content": "changed", "expected_sha256": "absent"},
            "oracle-requester",
            {"source": "protected-oracle", "case": "h-dedupe"},
            _now() + 7200,
            now=_now(),
        ),
        invariant,
        "changed request reused an existing idempotency key",
    )
    _assert(broker.claim("unapproved", now=_now()) is None, invariant, "unapproved request was claimable")
    _approve(broker, request_id, digest)
    claim = broker.claim("baseline-worker", now=_now(1))
    receipt = broker.execute_claim(claim, now=_now(2))
    required_receipt = {"filename", "before_sha256", "after_sha256", "bytes", "mode", "attempt", "request_digest"}
    _assert(isinstance(receipt, dict) and set(receipt) == required_receipt, invariant, "success receipt did not have the exact accepted shape")
    _assert(receipt["after_sha256"] == _sha("baseline") and receipt["mode"] == 384, invariant, "success receipt was not bound to verified filesystem state")
    target = workspace / "baseline.txt"
    _assert(target.read_text() == "baseline" and stat.S_IMODE(target.stat().st_mode) == 0o600, invariant, "approved effect was not exact and mode-bounded")

    outside = db_path.parent / "outside.txt"
    outside.write_text("outside")
    symlink = workspace / "link.txt"
    symlink.symlink_to(outside)
    symlink_id, symlink_digest = _propose(broker, "h-link", "link.txt", "overwrite", expected=_sha("outside"), at=_now(3))
    _approve(broker, symlink_id, symlink_digest, at=_now(3))
    symlink_claim = broker.claim("link-worker", now=_now(4))
    _expect_refusal(lambda: broker.execute_claim(symlink_claim, now=_now(5)), invariant, "symlink target was followed")
    _assert(outside.read_text() == "outside", invariant, "symlink execution mutated an out-of-workspace object")

    alt_workspace = db_path.parent / "alternate-workspace"
    alt_store = _new_store(db_path)
    alt_broker = _BROKER_CLASS(alt_store, alt_workspace, allowed_approvers={"merulox"}, approval_ttl_seconds=3600)
    _expect_refusal(alt_broker.initialize, invariant, "database reopened against a different workspace")
    _assert(not alt_workspace.exists(), invariant, "workspace binding refusal mutated alternate root")
    _close_store(alt_store)
    _close_store(store)

    schema_broker, schema_store, schema_db, schema_workspace = _new_broker("h-schema")
    _close_store(schema_store)
    _assert(_mutate_schema_marker_to_v2(schema_db), invariant, "schema-v3 initialization exposed no durable version marker")
    stale_store = _new_store(schema_db)
    stale_broker = _BROKER_CLASS(stale_store, schema_workspace, allowed_approvers={"merulox"}, approval_ttl_seconds=3600)
    try:
        stale_broker.initialize()
    except Exception as exc:
        text = str(exc).lower()
        _assert("reset" in text and ("schema" in text or "version" in text), invariant, "schema-v2 refusal lacked a clear reset-required error")
    else:
        _fail(invariant, "schema-v2 database was silently accepted or relabeled")
    finally:
        _close_store(stale_store)


def _case_i() -> None:
    invariant = "P02-I9"
    broker, _, _, workspace = _new_broker("i-lifecycle")
    filename = "lifecycle.txt"

    initial_id, initial_digest = _propose(broker, "i-initial", filename, "version-one", at=_now(0))
    _approve(broker, initial_id, initial_digest, at=_now(0))
    old_claim = broker.claim("expired-worker", lease_seconds=1, now=_now(1))
    _assert(old_claim is not None, invariant, "lifecycle could not obtain initial execution claim")
    old_attempt = _attempt_number(old_claim)
    broker.recover_expired(now=_now(3))
    retry_claim = broker.claim("retry-worker", lease_seconds=30, now=_now(4))
    _assert(retry_claim is not None and _attempt_number(retry_claim) > old_attempt, invariant, "expired lease recovery did not yield a newer retry")
    _expect_refusal(lambda: broker.execute_claim(old_claim, now=_now(5)), invariant, "expired older claim survived retry fencing")
    receipt = broker.execute_claim(retry_claim, now=_now(5))
    _assert(receipt["after_sha256"] == _sha("version-one"), invariant, "newer retry did not produce exact reviewed receipt")
    initial_state, initial_view = _state(broker, initial_id, invariant)
    _assert(initial_state == "succeeded" and _contains(initial_view, _sha("version-one")), invariant, "successful execution was not durably reviewable")

    cancelled_id, cancelled_digest = _propose(
        broker,
        "i-cancelled",
        filename,
        "never-applied",
        expected=_sha("version-one"),
        at=_now(6),
    )
    _approve(broker, cancelled_id, cancelled_digest, at=_now(6))
    cancelled_claim = broker.claim("cancelled-worker", now=_now(7))
    broker.cancel(cancelled_id, cancelled_digest, "merulox", "lifecycle cancellation", now=_now(8))
    _expect_refusal(lambda: broker.execute_claim(cancelled_claim, now=_now(9)), invariant, "lifecycle cancellation failed to fence old claim")
    _assert((workspace / filename).read_text() == "version-one", invariant, "cancellation-before-effect changed lifecycle file")

    outstanding_id, outstanding_digest = _propose(
        broker,
        "i-outstanding",
        filename,
        "takeover-blocked",
        expected=_sha("version-one"),
        at=_now(10),
    )
    _approve(broker, outstanding_id, outstanding_digest, at=_now(10))
    outstanding_claim = broker.claim("takeover-worker", now=_now(11))
    takeover = broker.takeover(filename, "merulox", "lifecycle takeover", now=_now(12))
    takeover_id = _takeover_id(takeover)
    _assert(_state(broker, outstanding_id, invariant)[0] == "cancelled", invariant, "takeover did not cancel lifecycle outstanding request")
    _expect_refusal(lambda: broker.execute_claim(outstanding_claim, now=_now(13)), invariant, "takeover failed to fence outstanding claim")
    _expect_refusal(
        lambda: _propose(
            broker,
            "i-during-takeover",
            filename,
            "forbidden",
            expected=_sha("version-one"),
            at=_now(14),
        ),
        invariant,
        "automatic proposal was accepted during lifecycle takeover",
    )
    broker.release_takeover(filename, takeover_id, "merulox", "lifecycle release", now=_now(15))

    fresh_id, fresh_digest = _propose(
        broker,
        "i-fresh",
        filename,
        "version-two",
        expected=_sha("version-one"),
        at=_now(16),
    )
    _approve(broker, fresh_id, fresh_digest, at=_now(16))
    fresh_claim = broker.claim("fresh-worker", now=_now(17))
    fresh_receipt = broker.execute_claim(fresh_claim, now=_now(18))
    _assert(fresh_receipt["after_sha256"] == _sha("version-two"), invariant, "fresh post-release execution lacked exact receipt")
    fresh_state, fresh_view = _state(broker, fresh_id, invariant)
    _assert(fresh_state == "succeeded" and _contains(fresh_view, fresh_receipt), invariant, "fresh post-release result was not durably reviewable")
    _assert(_state(broker, cancelled_id, invariant)[0] == "cancelled", invariant, "release revived pre-release cancelled request")
    _assert(_state(broker, outstanding_id, invariant)[0] == "cancelled", invariant, "release revived takeover-cancelled request")

    broker.rollback(fresh_id, fresh_digest, "merulox", now=_now(19))
    _assert((workspace / filename).read_text() == "version-one", invariant, "bounded rollback did not restore exact prior bytes")
    _assert(_state(broker, fresh_id, invariant)[0] == "rolled_back", invariant, "successful lifecycle rollback was not durable")

    conflict_id, conflict_digest = _propose(broker, "i-conflict", "conflict.txt", "broker-value", at=_now(20))
    _approve(broker, conflict_id, conflict_digest, at=_now(20))
    conflict_claim = broker.claim("conflict-worker", now=_now(21))
    broker.execute_claim(conflict_claim, now=_now(22))
    conflict_target = workspace / "conflict.txt"
    conflict_target.write_text("human-change")
    os.chmod(conflict_target, 0o600)
    _expect_refusal(
        lambda: broker.rollback(conflict_id, conflict_digest, "merulox", now=_now(23)),
        invariant,
        "rollback overwrote a conflicting post-success state",
    )
    _assert(conflict_target.read_text() == "human-change", invariant, "rollback containment did not preserve conflicting bytes")


def _case_j() -> None:
    invariant = "P02-I10"
    assert _ROOT is not None and _REPO is not None
    _assert(_ROOT.is_dir(), invariant, "disposable oracle root was unavailable")
    for child in _ROOT.iterdir():
        _assert(_inside(child, _ROOT), invariant, "oracle artifact escaped disposable root")
    origin = Path(getattr(_RUNTIME, "__file__")).resolve()
    _assert(_inside(origin, _REPO), invariant, "candidate import escaped supplied repository")


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValueError(message)


def _parse_args() -> argparse.Namespace:
    parser = _ArgumentParser(add_help=True)
    parser.add_argument("--repo", required=True, type=Path, help="candidate repository containing runtime_v2")
    return parser.parse_args()


def _emit(verdict: str, failure_class: str | None, invariant: str | None, counterexample: str | None) -> None:
    print(
        json.dumps(
            {
                "verdict": verdict,
                "failure_class": failure_class,
                "failed_public_invariant": invariant,
                "minimal_counterexample": counterexample,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def main() -> int:
    global _ROOT, _REPO
    try:
        args = _parse_args()
        repo = args.repo.expanduser().resolve(strict=True)
        if not repo.is_dir() or not (repo / "runtime_v2").is_dir():
            _emit("ESCALATE", "runner_failure", None, "--repo must identify a repository containing runtime_v2")
            return 2
    except (OSError, ValueError):
        _emit("ESCALATE", "runner_failure", None, "candidate repository path could not be resolved")
        return 2

    previous_cwd = Path.cwd()
    previous_env = {name: os.environ.get(name) for name in ("HOME", "TMPDIR", "XDG_CACHE_HOME", "PYTHONDONTWRITEBYTECODE")}
    try:
        with tempfile.TemporaryDirectory(prefix="k2-p02-oracle-") as raw_root:
            root = Path(raw_root).resolve()
            _ROOT = root
            _REPO = repo
            os.environ["HOME"] = str(root / "home")
            os.environ["TMPDIR"] = str(root / "tmp")
            os.environ["XDG_CACHE_HOME"] = str(root / "cache")
            os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
            for directory in (root / "home", root / "tmp", root / "cache"):
                directory.mkdir(mode=0o700)
            os.chdir(root)
            _install_containment(root)
            captured_output = io.StringIO()
            with contextlib.redirect_stdout(captured_output), contextlib.redirect_stderr(captured_output):
                _locate_runtime(repo)
                cases: tuple[tuple[str, Callable[[], None]], ...] = (
                    ("P02-I1", _case_a),
                    ("P02-I2", _case_b),
                    ("P02-I3", _case_c),
                    ("P02-I4", _case_d),
                    ("P02-I5", _case_e),
                    ("P02-I6", _case_f),
                    ("P02-I7", _case_g),
                    ("P02-I8", _case_h),
                    ("P02-I9", _case_i),
                    ("P02-I10", _case_j),
                )
                for invariant, case in cases:
                    try:
                        case()
                    except (ContractFailure, ContainmentViolation):
                        raise
                    except Exception as exc:
                        _fail(invariant, f"public scenario raised {type(exc).__name__}")
    except ContractFailure as exc:
        _emit("FAIL", "implementation_failure", exc.invariant, exc.counterexample)
        return 1
    except ContainmentViolation as exc:
        _emit("FAIL", "implementation_failure", "P02-I10", str(exc))
        return 1
    except (KeyboardInterrupt, SystemExit):
        _emit("ESCALATE", "runner_failure", None, "oracle execution was interrupted")
        return 2
    except Exception as exc:
        _emit("ESCALATE", "oracle_failure", None, f"oracle could not classify {type(exc).__name__}")
        return 2
    finally:
        try:
            os.chdir(previous_cwd)
        except OSError:
            pass
        for name, value in previous_env.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    _emit("PASS", None, None, None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
