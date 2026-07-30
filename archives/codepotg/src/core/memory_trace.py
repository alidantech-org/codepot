"""Low-overhead opt-in process and Python heap tracing."""

from __future__ import annotations

import ctypes
import json
import os
import sys
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path

from archives.codepotg.src.core.system_resources import detect_system_resources


@dataclass(frozen=True, slots=True)
class MemorySnapshot:
    stage: str
    elapsed_ms: float
    rss_bytes: int | None
    peak_rss_bytes: int | None
    private_bytes: int | None
    system_total_bytes: int | None
    system_available_bytes: int | None
    python_bytes: int | None
    python_peak_bytes: int | None

    def to_json(self) -> dict[str, object]:
        return asdict(self)

    def summary(self) -> str:
        values = [
            f"stage={self.stage}",
            f"elapsed={self.elapsed_ms:.1f}ms",
            f"rss={_format_bytes(self.rss_bytes)}",
            f"rss_peak={_format_bytes(self.peak_rss_bytes)}",
        ]
        if self.private_bytes is not None:
            values.append(f"private={_format_bytes(self.private_bytes)}")
        if self.system_available_bytes is not None:
            values.append(f"available={_format_bytes(self.system_available_bytes)}")
        if self.system_total_bytes is not None:
            values.append(f"total={_format_bytes(self.system_total_bytes)}")
        if self.python_bytes is not None:
            values.append(f"python={_format_bytes(self.python_bytes)}")
            values.append(f"python_peak={_format_bytes(self.python_peak_bytes)}")
        return "Memory trace: " + ", ".join(values)


class MemoryTrace:
    """Collect stage snapshots only when CODEPOTG_MEMORY_TRACE is enabled."""

    def __init__(
        self,
        *,
        enabled: bool,
        trace_allocations: bool = False,
        output_path: Path | None = None,
    ) -> None:
        self.enabled = enabled
        self.trace_allocations = trace_allocations
        self.output_path = output_path
        self.started_at = time.perf_counter()
        self.snapshots: list[MemorySnapshot] = []
        self._owns_tracemalloc = False
        if enabled and trace_allocations and not tracemalloc.is_tracing():
            tracemalloc.start(10)
            self._owns_tracemalloc = True

    @classmethod
    def from_environment(cls) -> MemoryTrace:
        raw = os.getenv("CODEPOTG_MEMORY_TRACE", "").strip().lower()
        enabled = raw not in {"", "0", "false", "off", "no"}
        trace_allocations = raw in {"full", "allocations", "tracemalloc"}
        output = os.getenv("CODEPOTG_MEMORY_TRACE_FILE", "").strip()
        return cls(
            enabled=enabled,
            trace_allocations=trace_allocations,
            output_path=Path(output).expanduser() if output else None,
        )

    def snapshot(self, stage: str) -> MemorySnapshot | None:
        if not self.enabled:
            return None
        rss, peak_rss, private = _process_memory()
        resources = detect_system_resources()
        python_current: int | None = None
        python_peak: int | None = None
        if tracemalloc.is_tracing():
            python_current, python_peak = tracemalloc.get_traced_memory()
        snapshot = MemorySnapshot(
            stage=stage,
            elapsed_ms=(time.perf_counter() - self.started_at) * 1000,
            rss_bytes=rss,
            peak_rss_bytes=peak_rss,
            private_bytes=private,
            system_total_bytes=resources.total_memory,
            system_available_bytes=resources.available_memory,
            python_bytes=python_current,
            python_peak_bytes=python_peak,
        )
        self.snapshots.append(snapshot)
        self._write(snapshot)
        return snapshot

    def summaries(self) -> tuple[str, ...]:
        return tuple(snapshot.summary() for snapshot in self.snapshots)

    def close(self) -> None:
        if self._owns_tracemalloc and tracemalloc.is_tracing():
            tracemalloc.stop()
            self._owns_tracemalloc = False

    def _write(self, snapshot: MemorySnapshot) -> None:
        if self.output_path is None:
            return
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(snapshot.to_json(), sort_keys=True))
            stream.write("\n")


def _process_memory() -> tuple[int | None, int | None, int | None]:
    if sys.platform == "win32":
        return _windows_memory()
    if sys.platform.startswith("linux"):
        return _linux_memory()
    return _resource_memory()


def _windows_memory() -> tuple[int | None, int | None, int | None]:
    try:
        class ProcessMemoryCountersEx(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong),
                ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCountersEx()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        get_process = kernel32.GetCurrentProcess
        get_process.argtypes = []
        get_process.restype = ctypes.c_void_p
        get_memory = psapi.GetProcessMemoryInfo
        get_memory.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ProcessMemoryCountersEx),
            ctypes.c_ulong,
        ]
        get_memory.restype = ctypes.c_int
        process = get_process()
        if not get_memory(process, ctypes.byref(counters), counters.cb):
            return None, None, None
        return (
            int(counters.WorkingSetSize),
            int(counters.PeakWorkingSetSize),
            int(counters.PrivateUsage),
        )
    except (AttributeError, OSError, TypeError, ValueError):
        return None, None, None


def _linux_memory() -> tuple[int | None, int | None, int | None]:
    try:
        values: dict[str, int] = {}
        with Path("/proc/self/status").open("r", encoding="utf-8") as stream:
            for line in stream:
                name, separator, raw = line.partition(":")
                if not separator or name not in {"VmRSS", "VmHWM", "VmData"}:
                    continue
                amount = raw.strip().split()[0]
                values[name] = int(amount) * 1024
        return values.get("VmRSS"), values.get("VmHWM"), values.get("VmData")
    except (OSError, ValueError, IndexError):
        return _resource_memory()


def _resource_memory() -> tuple[int | None, int | None, int | None]:
    try:
        import resource

        maximum = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform != "darwin":
            maximum *= 1024
        return None, maximum, None
    except (ImportError, OSError, ValueError):
        return None, None, None


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "n/a"
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f}{unit}"
        amount /= 1024
    return f"{amount:.1f}GiB"
