"""Emission template constants."""

# Template file extension
TEMPLATE_EXTENSION = ".j2"

# Path token patterns
TOKEN_SEGMENT_PREFIX = "["
TOKEN_SEGMENT_SUFFIX = "]"
TOKEN_SPREAD_PREFIX = "[..."
TOKEN_SPREAD_SUFFIX = "]"
TOKEN_INLINE_PREFIX = "("
TOKEN_INLINE_SUFFIX = ")"

# Token regex patterns
SEGMENT_PATTERN = r"^\[([a-zA-Z_][a-zA-Z0-9_.]*)\]$"
SPREAD_PATTERN = r"^\[\.\.\.([a-zA-Z_][a-zA-Z0-9_.]*)\]$"
INLINE_PATTERN = r"\(([a-zA-Z_][a-zA-Z0-9_.]*)\)"

# Combined variable pattern for descriptor
VARIABLE_PATTERN = r"\[\.\.\.([a-zA-Z_][a-zA-Z0-9_.]*)\]" r"|\[([a-zA-Z_][a-zA-Z0-9_.]*)\]" r"|\(([a-zA-Z_][a-zA-Z0-9_.]*)\)"

# Owner namespace prefixes for classification
OWNER_PREFIX_DTO = "dto."
OWNER_PREFIX_OPERATION = "operation."
OWNER_PREFIX_SCHEMA = "schema."
OWNER_PREFIX_RESOURCE = "resource."
OWNER_PREFIX_BARREL = "barrel."
OWNER_PREFIX_FIELD = "field."

# Owner priority order (higher priority first)
OWNER_PRIORITY_ORDER = (
    OWNER_PREFIX_DTO,
    OWNER_PREFIX_OPERATION,
    OWNER_PREFIX_SCHEMA,
    OWNER_PREFIX_RESOURCE,
    OWNER_PREFIX_BARREL,
    OWNER_PREFIX_FIELD,
)
