KNOWN_SUFFIXES = tuple(
    sorted((".cts", ".d.cts", ".d.mts", ".d.ts", ".mts", ".ts", ".tsx"))
)


def match_typescript_suffix(path: str) -> str | None:
    for suffix in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if path.endswith(suffix):
            return suffix
    return None


def strip_typescript_suffix(path: str) -> str:
    suffix = match_typescript_suffix(path)
    return path[: -len(suffix)] if suffix else path
