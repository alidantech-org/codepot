"""Shared emission engine for template-driven code generation.

Emission owns template scanning, path expansion, rendering, and final output
planning. Language modules prepare contexts; emission consumes those contexts.
"""
