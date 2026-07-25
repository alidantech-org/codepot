"""Adaptive CPU and memory budgets for large CodepotG workloads."""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass
from pathlib import Path

_MIB = 1024 * 1024
_GIB = 1024 * _MIB


@dataclass(frozen=True, slots=True)
class SystemResources:
    """Current host capacity used for bounded performance tuning."""

    cpu_count: int
    total_memory: int | None
    available_memory: int | None

    @property
    def usable_memory(self) -> int:
        """Return a conservative available-memory estimate."""
        if self.available_memory is not None:
            return max(self.available_memory, 64 * _MIB)
        if self.total_memory is not None:
            return max(self.total_memory // 2, 64 * _MIB)
        return 512 * _MIB


@dataclass(frozen=True, slots=True)
class RuntimeTuning:
    """Resolved queue, cache, and worker limits for one workload."""

    source_bytes: int
    cpu_count: int
    total_memory: int | None
    available_memory: int | None
    hot_index_entries: int
    hot_index_bytes: int
    jsonl_pending_records: int
    jsonl_pending_bytes: int
    jsonl_event_queue: int
    sqlite_cache_bytes: int
    render_workers: int
    write_workers: int
    pending_files: int
    pending_render_bytes: int
    write_batch_files: int
    write_batch_bytes: int

    def summary(self) -> str:
        return (
            "Runtime tuning: "
            f"cpus={self.cpu_count}, "
            f"available={_format_bytes(self.available_memory)}, "
            f"source={_format_bytes(self.source_bytes)}, "
            f"jsonl_records={self.jsonl_pending_records}, "
            f"jsonl_bytes={_format_bytes(self.jsonl_pending_bytes)}, "
            f"sqlite_cache={_format_bytes(self.sqlite_cache_bytes)}, "
            f"render_workers={self.render_workers}, "
            f"write_workers={self.write_workers}, "
            f"write_batch={self.write_batch_files}/"
            f"{_format_bytes(self.write_batch_bytes)}"
        )


def detect_system_resources() -> SystemResources:
    """Read CPU count and current memory availability without third-party packages."""
    cpu_count = max(1, os.cpu_count() or 1)
    total: int | None = None
    available: int | None = None
    if sys.platform == "win32":
        total, available = _windows_memory_status()
    elif sys.platform.startswith("linux"):
        total, available = _linux_memory_status()
    elif sys.platform == "darwin":
        total, available = _posix_memory_status()
    else:
        total, available = _posix_memory_status()
    return SystemResources(
        cpu_count=cpu_count,
        total_memory=total,
        available_memory=available,
    )


def tune_runtime(
    source: str | Path | int,
    *,
    planned_files: int | None = None,
) -> RuntimeTuning:
    """Derive speed-oriented bounds from source size and current free memory."""
    source_bytes = (
        max(0, source)
        if isinstance(source, int)
        else _safe_file_size(Path(source))
    )
    resources = detect_system_resources()
    usable = resources.usable_memory

    # Use RAM aggressively enough to avoid tiny queues, but never reserve more than
    # a quarter of what is currently available for one CodepotG phase.
    phase_budget = _clamp(usable // 4, 128 * _MIB, 2 * _GIB)
    source_factor = _clamp(max(source_bytes * 4, 64 * _MIB), 64 * _MIB, phase_budget)

    hot_index_bytes = _clamp(phase_budget // 8, 32 * _MIB, 256 * _MIB)
    sqlite_cache_bytes = _clamp(phase_budget // 6, 32 * _MIB, 512 * _MIB)
    jsonl_pending_bytes = _clamp(source_factor, 64 * _MIB, min(phase_budget, 512 * _MIB))
    pending_render_bytes = _clamp(phase_budget // 3, 64 * _MIB, 512 * _MIB)
    write_batch_bytes = _clamp(phase_budget // 32, 4 * _MIB, 32 * _MIB)

    render_workers = _env_int(
        "CODEPOTG_RENDER_WORKERS",
        _clamp(resources.cpu_count, 2, 12),
        minimum=1,
        maximum=64,
    )
    write_workers = _env_int(
        "CODEPOTG_WRITE_WORKERS",
        _clamp(max(2, resources.cpu_count // 2), 2, 8),
        minimum=1,
        maximum=32,
    )
    estimated_files = max(1, planned_files or 64)
    pending_files = _clamp(
        max(render_workers * 8, min(estimated_files, 128)),
        16,
        256,
    )
    write_batch_files = _env_int(
        "CODEPOTG_WRITE_BATCH_FILES",
        _clamp(write_workers * 8, 16, 64),
        minimum=1,
        maximum=512,
    )

    return RuntimeTuning(
        source_bytes=source_bytes,
        cpu_count=resources.cpu_count,
        total_memory=resources.total_memory,
        available_memory=resources.available_memory,
        hot_index_entries=_clamp(hot_index_bytes // 1024, 16_384, 262_144),
        hot_index_bytes=hot_index_bytes,
        jsonl_pending_records=_clamp(jsonl_pending_bytes // (256 * 1024), 64, 2048),
        jsonl_pending_bytes=jsonl_pending_bytes,
        jsonl_event_queue=256,
        sqlite_cache_bytes=sqlite_cache_bytes,
        render_workers=render_workers,
        write_workers=write_workers,
        pending_files=pending_files,
        pending_render_bytes=pending_render_bytes,
        write_batch_files=write_batch_files,
        write_batch_bytes=write_batch_bytes,
    )


def _windows_memory_status() -> tuple[int | None, int | None]:
    try:
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        function = kernel32.GlobalMemoryStatusEx
        function.argtypes = [ctypes.POINTER(MemoryStatusEx)]
        function.restype = ctypes.c_int
        if not function(ctypes.byref(status)):
            return None, None
        return int(status.ullTotalPhys), int(status.ullAvailPhys)
    except (AttributeError, OSError, ValueError):
        return None, None


def _linux_memory_status() -> tuple[int | None, int | None]:
    try:
        values: dict[str, int] = {}
        with Path("/proc/meminfo").open("r", encoding="utf-8") as stream:
            for line in stream:
                name, separator, raw = line.partition(":")
                if not separator or name not in {"MemTotal", "MemAvailable", "MemFree"}:
                    continue
                values[name] = int(raw.strip().split()[0]) * 1024
        return values.get("MemTotal"), values.get("MemAvailable", values.get("MemFree"))
    except (OSError, ValueError, IndexError):
        return _posix_memory_status()


def _posix_memory_status() -> tuple[int | None, int | None]:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        total_pages = os.sysconf("SC_PHYS_PAGES")
        available_pages = os.sysconf("SC_AVPHYS_PAGES")
        return int(page_size * total_pages), int(page_size * available_pages)
    except (AttributeError, OSError, ValueError):
        return None, None


def _safe_file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def _env_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return _clamp(int(raw), minimum, maximum)
    except ValueError:
        return default


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "unknown"
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if amount < 1024 or unit == "GiB":
            return f"{amount:.1f}{unit}"
        amount /= 1024
    return f"{amount:.1f}GiB"
