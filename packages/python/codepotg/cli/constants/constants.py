"""CLI constants and help text.

This module is owned by the CLI adapter. Runtime and engine modules must not
import from it.
"""

APP_NAME = "codepotg"
APP_DESCRIPTION = "Stable OpenAPI-driven Python and Jinja Codepot generator."
APP_VERSION = "1.0.0"

CMD_EMIT = "emit"
CMD_GENERATE = "generate"
CMD_INIT = "init"
CMD_TASK = "task"
CMD_INFER = "infer"
CMD_INSPECT = "inspect"
CMD_VALIDATE = "validate"

OPT_INPUT = "input"
OPT_OUTPUT = "output"
OPT_LANGUAGE = "language"
OPT_TEMPLATES = "templates"
OPT_DRY_RUN = "dry-run"
OPT_INTERACTIVE = "interactive"
OPT_DEBUG = "debug"
OPT_VERBOSE = "verbose"
OPT_QUIET = "quiet"
OPT_VERSION = "version"

HELP_INPUT = "Input OpenAPI document."
HELP_OUTPUT = "Output directory or file, depending on the command."
HELP_OUTPUT_INFERENCE = "Optional inference JSON output path."
HELP_LANGUAGE = "Target language, for example debug, dart, or typescript."
HELP_TEMPLATES_PATH = "Custom template root. Omit it to use the bundled language pack."
HELP_DRY_RUN = "Plan output without writing generated files."
HELP_INTERACTIVE = "Prompt for missing command options interactively."
HELP_DEBUG = "Show traceback when an error occurs."
HELP_VERBOSE = "Show detailed CLI output."
HELP_QUIET = "Suppress normal CLI output."
HELP_VERSION = "Show version and exit."

HELP_EMIT = "Emit output for a target language."
HELP_GENERATE = "Run Codepotg.yaml task generation."
HELP_INIT = "Create Codepotg.yaml."
HELP_TASK = "Edit Codepotg.yaml tasks."
HELP_INFER = "Run inference and optionally write inference JSON."
HELP_INSPECT = "Inspect an OpenAPI document."
HELP_VALIDATE = "Validate an OpenAPI document."
