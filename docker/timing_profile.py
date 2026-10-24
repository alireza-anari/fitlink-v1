"""Finite numeric delegation timers. No arguments, results or exception text."""

import functools
import threading
import time

LABELS = frozenset(
    {
        "state_clone",
        "model_reload",
        "models_reload",
        "model_render",
        "migration_execute",
        "migration_apply",
        "migration_unapply",
        "migration_state",
        "corpus",
        "verification_fixture",
        "publication_prepare",
        "publication_confirm",
        "projection_refresh",
        "unpublish",
        "search",
        "reconcile",
        "install",
        "control",
    }
)
PHASES = frozenset({"session", "setup", "call", "teardown"})


class Tracker:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.phase = "session"
        self.ordinal = 0
        self.local = threading.local()
        self.lock = threading.Lock()
        self.stats = {}
        self.registered = set()
        self.fault = False
        self.overhead_wall_ns = self.overhead_cpu_ns = 0

    def context(self, phase, ordinal):
        if phase not in PHASES or type(ordinal) is not int or not 0 <= ordinal <= 100:
            self.fault = True
            return
        self.phase, self.ordinal = phase, ordinal

    def wrap(self, label, original):
        if label not in LABELS:
            raise ValueError("unknown_timer_label")

        with self.lock:
            self.registered.add(label)

        @functools.wraps(original)
        def delegate(*args, **kwargs):
            if not self.enabled or self.fault:
                return original(*args, **kwargs)
            frame = None
            try:
                begin = time.monotonic_ns()
                cpu_begin = time.thread_time_ns()
                stack = getattr(self.local, "stack", None)
                if stack is None:
                    stack = self.local.stack = []
                frame = {
                    "key": (label, self.phase, self.ordinal),
                    "child_wall": 0,
                    "child_cpu": 0,
                }
                stack.append(frame)
                wall = time.monotonic_ns()
                cpu = time.thread_time_ns()
            except Exception:
                self.fault = True
                frame = None
            try:
                return original(*args, **kwargs)
            finally:
                if frame is not None:
                    try:
                        cpu_end = time.thread_time_ns()
                        end = time.monotonic_ns()
                        elapsed = end - wall
                        consumed = cpu_end - cpu
                        stack = self.local.stack
                        if not stack or stack.pop() is not frame:
                            raise ValueError("timer_stack_mismatch")
                        if stack:
                            stack[-1]["child_wall"] += elapsed
                            stack[-1]["child_cpu"] += consumed
                        with self.lock:
                            if (
                                len(self.stats) >= 2048
                                and frame["key"] not in self.stats
                            ):
                                self.fault = True
                            else:
                                value = self.stats.setdefault(
                                    frame["key"],
                                    {
                                        "count": 0,
                                        "wall_ns": 0,
                                        "cpu_ns": 0,
                                        "self_wall_ns": 0,
                                        "self_cpu_ns": 0,
                                        "first_start_ns": wall,
                                        "last_end_ns": end,
                                    },
                                )
                                value["first_start_ns"] = min(
                                    value["first_start_ns"], wall
                                )
                                value["last_end_ns"] = max(value["last_end_ns"], end)
                                value["count"] += 1
                                value["wall_ns"] += elapsed
                                value["cpu_ns"] += consumed
                                value["self_wall_ns"] += max(
                                    0, elapsed - frame["child_wall"]
                                )
                                value["self_cpu_ns"] += max(
                                    0, consumed - frame["child_cpu"]
                                )
                        # Measured bookkeeping segment excludes final counter update.
                        overhead_wall = time.monotonic_ns() - begin - elapsed
                        overhead_cpu = time.thread_time_ns() - cpu_begin - consumed
                        with self.lock:
                            self.overhead_wall_ns += max(0, overhead_wall)
                            self.overhead_cpu_ns += max(0, overhead_cpu)
                    except Exception:
                        self.fault = True

        return delegate

    def report(self):
        with self.lock:
            return {
                "enabled": self.enabled,
                "fault": self.fault,
                "registered_labels": sorted(self.registered) if self.enabled else None,
                "cpu_clock": "thread_time_ns",
                "inclusive_times_overlap": True,
                "self_definition": (
                    "delegate minus timed descendants; includes recorder overhead"
                ),
                "bookkeeping_wall_ns": self.overhead_wall_ns if self.enabled else None,
                "bookkeeping_cpu_ns": self.overhead_cpu_ns if self.enabled else None,
                "rows": [
                    {"label": label, "phase": phase, "ordinal": ordinal, **v}
                    for (label, phase, ordinal), v in sorted(self.stats.items())
                ]
                if self.enabled
                else None,
            }


def install_migrations(tracker):
    from django.db.migrations.executor import MigrationExecutor
    from django.db.migrations.loader import MigrationLoader
    from django.db.migrations.migration import Migration
    from django.db.migrations.state import ProjectState, StateApps

    saved = []
    targets = [
        (ProjectState, "clone", "state_clone"),
        (ProjectState, "reload_model", "model_reload"),
        (ProjectState, "reload_models", "models_reload"),
        (StateApps, "render_multiple", "model_render"),
        (MigrationExecutor, "migrate", "migration_execute"),
        (Migration, "apply", "migration_apply"),
        (Migration, "unapply", "migration_unapply"),
        (MigrationLoader, "project_state", "migration_state"),
    ]
    try:
        for owner, name, label in targets:
            original = getattr(owner, name)
            saved.append((owner, name, original))
            setattr(owner, name, tracker.wrap(label, original))
    except BaseException:
        restore(saved)
        raise
    return saved


def restore(saved):
    for owner, name, original in reversed(saved):
        setattr(owner, name, original)


def install_lifecycle(tracker, item):
    # Called after fixture setup; both full/minimal controls import the same
    # function-only gateways here. Import cost is inside pytest call timing.
    import importlib

    saved = []
    previous = None
    try:
        for module_name, name, label in [
            (
                "config.use_cases.publication",
                "prepare_publication",
                "publication_prepare",
            ),
            (
                "config.use_cases.publication",
                "confirm_publication",
                "publication_confirm",
            ),
            ("config.use_cases.publication", "unpublish_profile", "unpublish"),
            (
                "config.use_cases.marketplace",
                "refresh_public_projection",
                "projection_refresh",
            ),
            ("config.use_cases.marketplace", "search_public_professionals", "search"),
            ("config.use_cases.marketplace", "reconcile_publications", "reconcile"),
            (
                "tests.integration.c04.search_helpers",
                "coach_approved",
                "verification_fixture",
            ),
        ]:
            owner = importlib.import_module(module_name)
            original = getattr(owner, name)
            if tracker.enabled:
                saved.append((owner, name, original))
                setattr(owner, name, tracker.wrap(label, original))
        if "corpus" in item.funcargs and tracker.enabled:
            previous = item.funcargs["corpus"]
            item.funcargs["corpus"] = tracker.wrap("corpus", previous)
    except BaseException:
        restore(saved)
        if previous is not None:
            item.funcargs["corpus"] = previous
        raise
    return saved, previous


def calibration():
    tracker = Tracker()
    wrapped = tracker.wrap("control", lambda: None)
    wall = time.monotonic_ns()
    cpu = time.thread_time_ns()
    for _ in range(10000):
        wrapped()
    return {
        "calls": 10000,
        "wall_ns": time.monotonic_ns() - wall,
        "cpu_ns": time.thread_time_ns() - cpu,
        "fault": tracker.fault,
    }
