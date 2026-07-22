"""
Command workflow orchestration package.

This package contains workflow functions that orchestrate the full pipeline for
each CLI command: inspect, infer, emit, and validate. Each workflow loads documents,
runs inference, creates emission plans, and delegates to presenters for output.
"""
