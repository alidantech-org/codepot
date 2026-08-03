"""HTTP protocol constants."""

# HTTP methods
GET = "get"
POST = "post"
PUT = "put"
PATCH = "patch"
DELETE = "delete"
OPTIONS = "options"
HEAD = "head"
TRACE = "trace"

HTTP_METHODS = {GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, TRACE}

# Content types
CONTENT_JSON = "application/json"
CONTENT_FORM_DATA = "multipart/form-data"
CONTENT_TEXT = "text/plain"

# Status codes
STATUS_DEFAULT = "default"
DEFAULT_STATUS_CODE = "default"
STATUS_SUCCESS_MIN = 200
STATUS_SUCCESS_MAX = 299
STATUS_ERROR_MIN = 400
