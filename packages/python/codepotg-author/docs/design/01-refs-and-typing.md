# Typed refs and authoring safety

## Ref categories

Planned refs are immutable, author-session-bound values:

```text
GroupRef
PropertyRef[T]
SchemaRef[T]
FieldRef[T]
OperationRef[TInput, TOutput]
PolicyRef
EventRef[TPayload]
StorageRef[T]
ValueSourceRef[T]
ViewRef
PresentationRef
WorkflowRef
WorkflowStepRef
```

This is type-notation used by the design. The package targets Python 3.11, so implementation must use `TypeVar`, `Generic`, protocols, and overloads. Do not use Python 3.12-only PEP 695 declarations such as `class SchemaRef[T]` unless the package's minimum Python version is intentionally changed through a separate approved decision.

A wrong ref kind is rejected both statically where possible and by the runtime linker.

## Identity

A ref contains only author/linker identity and typed kind information. It is not a final JSON `$ref` and is not directly serialized.

```python
@dataclass(frozen=True, slots=True)
class RefIdentity:
    author_id: str
    declaration_id: str
    kind: RefKind
```

Final core relations use `SemanticId`. Canonical transport uses portable `$ref` objects.

## Usage wrappers

Ref usage is separate from identity:

```python
User.optional()
User.nullable()
User.array()
```

Each call returns an immutable usage object containing the base ref and use-specific facts. Chaining must be deterministic and must not mutate the target definition.

## Typed field selection

Python cannot derive arbitrary field-name `Literal` unions as freely as TypeScript. Prefer typed selector lambdas over raw strings:

```python
User.pick("UserRead", lambda f: (f.id, f.email, f.display_name))
```

The selector argument is statically typed as the source model. Runtime invocation uses a restricted proxy that produces `FieldRef` values only. Unknown attributes and foreign-field refs are errors.

## Forward refs

Forward declarations are explicit and typed:

```python
notify = workflow.declare_step("notify")
create.then(notify)
workflow.define_step(notify, operation=send_email)
```

Compilation fails when a forward ref remains undefined, changes kind, is defined twice, or belongs to another author session.

## Static checking

Required typing gates:

- strict Pyright configuration;
- strict mypy configuration or documented supported subset;
- positive fixtures that type-check;
- negative fixtures for wrong ref kinds, wrong builder arguments, unknown field selectors, and incompatible workflow transitions;
- no reliance on runtime-only `Any` for public ref APIs.

A custom mypy/Pyright plugin or generated `.pyi` files are future optimizations, not requirements for the first usable ref engine.
