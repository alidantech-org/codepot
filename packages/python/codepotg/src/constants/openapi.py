"""Standard OpenAPI specification constants."""

# Root keys
OPENAPI = "openapi"
INFO = "info"
TITLE = "title"
VERSION = "version"
PATHS = "paths"
COMPONENTS = "components"
SERVERS = "servers"
URL = "url"
VARIABLES = "variables"

# Component sections
SCHEMAS = "schemas"
RESPONSES = "responses"
REQUEST_BODIES = "requestBodies"
PARAMETERS = "parameters"
HEADERS = "headers"
EXAMPLES = "examples"
SECURITY_SCHEMES = "securitySchemes"

# Operation keys
OPERATION_ID = "operationId"
PARAMETERS = "parameters"
REQUEST_BODY = "requestBody"
RESPONSES = "responses"
DESCRIPTION = "description"
SUMMARY = "summary"
REQUIRED = "required"

# Content keys
CONTENT = "content"
SCHEMA = "schema"

# Reference keys
REF = "$ref"

# Reference prefixes
JSON_POINTER_PREFIX = "#/"
COMPONENT_REF_PREFIX = "#/components/"

# Component reference paths
REF_SCHEMAS = f"{COMPONENT_REF_PREFIX}{SCHEMAS}/"
REF_RESPONSES = f"{COMPONENT_REF_PREFIX}{RESPONSES}/"
REF_REQUEST_BODIES = f"{COMPONENT_REF_PREFIX}{REQUEST_BODIES}/"
REF_PARAMETERS = f"{COMPONENT_REF_PREFIX}{PARAMETERS}/"

# x-codegen keys
X_CODEGEN_RESOURCE = "resource"
X_CODEGEN_NAME = "name"
X_CODEGEN_PATH = "path"

# Schema keys
TYPE = "type"
PROPERTIES = "properties"
ALL_OF = "allOf"
ANY_OF = "anyOf"
ONE_OF = "oneOf"
ENUM = "enum"
ITEMS = "items"
FORMAT = "format"
DEFAULT = "default"

# Internal keys
RAW = "raw"

# Schema type values
TYPE_OBJECT = "object"
TYPE_STRING = "string"
TYPE_INTEGER = "integer"
TYPE_NUMBER = "number"
TYPE_BOOLEAN = "boolean"
TYPE_NULL = "null"
TYPE_ARRAY = "array"

# Composition kinds
COMPOSITION_ALL_OF = "allOf"
COMPOSITION_ANY_OF = "anyOf"
COMPOSITION_ONE_OF = "oneOf"

# Parameter keys
PARAM_NAME = "name"
PARAM_IN = "in"

# HTTP status codes
STATUS_DEFAULT = "default"
STATUS_SUCCESS_MIN = 200
STATUS_SUCCESS_MAX = 300
STATUS_ERROR_MIN = 400

# Default values
DEFAULT_TITLE = "Untitled API"

# Dependency source prefixes
OPERATION_PREFIX = "operation:"

# Error messages
ERR_FILE_NOT_FOUND = "OpenAPI file does not exist: {path}"
ERR_NOT_A_FILE = "OpenAPI path is not a file: {path}"
ERR_UNSUPPORTED_EXTENSION = "Unsupported OpenAPI file extension '{suffix}'. Use .yaml, .yml, or .json."
ERR_LOAD_FAILED = "Failed to load OpenAPI document: {path}"
ERR_ROOT_NOT_OBJECT = "OpenAPI document root must be an object."
ERR_MISSING_OPENAPI = "OpenAPI document is missing required 'openapi' field."
ERR_MISSING_PATHS = "OpenAPI document is missing required 'paths' field."

# Component sections list
COMPONENT_SECTIONS = (
    SCHEMAS,
    RESPONSES,
    REQUEST_BODIES,
    PARAMETERS,
    HEADERS,
    EXAMPLES,
    SECURITY_SCHEMES,
)
