"""Application orchestration package.

This package exposes the public GeneratorApp API and app workflows used by CLI,
tests, UI adapters, or other external interfaces.
"""

from .app import GeneratorApp

__all__ = ["GeneratorApp"]
