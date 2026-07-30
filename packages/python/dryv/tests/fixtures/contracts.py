from __future__ import annotations

from dryv.ir import (
    AccessFacet,
    Compensation,
    Contract,
    Event,
    EventEffect,
    EventsFacet,
    FieldConstraints,
    Group,
    Name,
    Operation,
    OperationEffects,
    OperationFacets,
    OperationOutput,
    Policy,
    Schema,
    SchemaField,
    SchemaKind,
    SchemaUse,
    SemanticId,
    StorageFieldMapping,
    StorageMapping,
    TriggerFacet,
    TriggerKind,
    TypeExpression,
    View,
    ViewTrigger,
    Workflow,
    WorkflowStep,
    WorkflowStepKind,
    WorkflowTransition,
)


def sid(value: str) -> SemanticId:
    return SemanticId(value)


def build_connected_contract() -> Contract:
    user_id = sid("identity.schema.user")
    user_field_id = sid("identity.schema.user.field.id")
    user_email_id = sid("identity.schema.user.field.email")
    created_event = sid("identity.event.user_created")
    create_operation = sid("identity.operation.create_user")
    delete_operation = sid("identity.operation.delete_user")
    listener_operation = sid("identity.operation.audit_user_created")
    policy_id = sid("identity.policy.manage_users")

    user = Schema(
        id=user_id,
        name=Name("User"),
        kind=SchemaKind.OBJECT,
        fields=(
            SchemaField(
                id=user_field_id,
                name=Name("id"),
                type=TypeExpression.primitive("string"),
                required=True,
                readonly=True,
            ),
            SchemaField(
                id=user_email_id,
                name=Name("email"),
                type=TypeExpression.primitive("string"),
                required=True,
                constraints=FieldConstraints(format="email", max_length=320),
            ),
        ),
    )

    event = Event(id=created_event, name=Name("UserCreated"), payload_schema=user_id)
    policy = Policy(id=policy_id, name=Name("ManageUsers"), permissions=("users.manage",))

    create_user = Operation(
        id=create_operation,
        name=Name("CreateUser"),
        inputs=(SchemaUse(name=Name("request"), schema=user_id, required=True),),
        outputs=(OperationOutput(name=Name("user"), schema=user_id),),
        effects=OperationEffects(
            events=(EventEffect(event=created_event, payload_schema=user_id),)
        ),
        facets=OperationFacets(
            access=AccessFacet(effective=(policy_id,), authenticated=True),
        ),
    )
    delete_user = Operation(
        id=delete_operation,
        name=Name("DeleteUser"),
        inputs=(SchemaUse(name=Name("user"), schema=user_id, required=True),),
    )
    audit_listener = Operation(
        id=listener_operation,
        name=Name("AuditUserCreated"),
        inputs=(SchemaUse(name=Name("event"), schema=user_id, required=True),),
        facets=OperationFacets(
            trigger=TriggerFacet(kind=TriggerKind.EVENT, event=created_event),
            events=EventsFacet(consumes=(created_event,)),
        ),
    )

    storage = StorageMapping(
        id=sid("identity.storage.user"),
        name=Name("UserStorage"),
        schema=user_id,
        source="users",
        fields=(
            StorageFieldMapping(field=user_field_id, column="id", column_type="uuid", unique=True),
            StorageFieldMapping(
                field=user_email_id,
                column="email",
                column_type="varchar",
                unique=True,
            ),
        ),
        primary_key=(user_field_id,),
        indexes=((user_email_id,),),
    )

    view = View(
        id=sid("identity.view.create_user"),
        name=Name("CreateUserView"),
        schema=user_id,
        triggers=(
            ViewTrigger(
                name=Name("Submit"),
                operation=create_operation,
                interaction="submit",
                payload_schema=user_id,
            ),
        ),
        access=AccessFacet(effective=(policy_id,), authenticated=True),
    )

    workflow = Workflow(
        id=sid("identity.workflow.register_user"),
        name=Name("RegisterUser"),
        inputs=(SchemaUse(name=Name("request"), schema=user_id, required=True),),
        outputs=(OperationOutput(name=Name("user"), schema=user_id),),
        steps=(
            WorkflowStep(
                name="create",
                kind=WorkflowStepKind.OPERATION,
                operation=create_operation,
                compensation=Compensation(operation=delete_operation),
            ),
            WorkflowStep(name="complete", kind=WorkflowStepKind.END),
        ),
        transitions=(WorkflowTransition(source="create", target="complete"),),
    )

    group = Group(
        id=sid("identity.group.users"),
        name=Name("Users"),
        path=("identity", "users"),
        schemas=(user,),
        operations=(create_user, delete_user, audit_listener),
        views=(view,),
        storage_mappings=(storage,),
        workflows=(workflow,),
        policies=(policy,),
        events=(event,),
    )
    return Contract(
        id=sid("application.identity"),
        name=Name("IdentityApplication"),
        groups=(group,),
    )
