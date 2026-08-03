"""CLI-specific errors."""


class CliError(Exception):
    exit_code = 1


class ConfigError(CliError):
    exit_code = 3


class ValidationCliError(CliError):
    exit_code = 1


class GenerationCliError(CliError):
    exit_code = 2
