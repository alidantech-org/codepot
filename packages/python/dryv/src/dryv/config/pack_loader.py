"""Task-21 compatibility adapter for Pack Feature decoding."""

from dryv.features.packs import PackConfigurationError, PackManifest
from dryv.features.packs import decode_pack_manifest as _decode_pack_manifest


def decode_pack_manifest(value: object) -> PackManifest:
    return _decode_pack_manifest(value)


__all__ = ["PackConfigurationError", "PackManifest", "decode_pack_manifest"]
