"""Normalized spec context contracts.

These contracts wrap the typed compiled IR models with runtime metadata used by
the repository, planner, language adapters, and templates.

The actual YAML/spec data remains in ``spec.ir`` typed models. These contracts
only add normalized keys, names, refs, ownership, dependencies, and record sets.
"""
