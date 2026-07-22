"""Tests for Jinja template rendering."""

from __future__ import annotations

from pathlib import Path

from src.emission.templates.renderer import render_template


def test_render_template_uses_contract_context(tmp_path: Path) -> None:
    template_root = tmp_path / "templates"
    template_root.mkdir()
    template = template_root / "hello.txt.j2"
    template.write_text("Hello {{ name }}", encoding="utf-8")

    output = render_template(
        template_root=template_root,
        relative_path=Path("hello.txt.j2"),
        context={"name": "World"},
    )

    assert output == "Hello World"


def test_dart_version_barrel_exports_match_path_config(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "dart",
        relative_path=Path("{version}") / "v1.dart.j2",
        context={
            "schemas": {
                "emit_models": [
                    {
                        "emit": {"resource_path": ("platform", "auth", "users")},
                        "name": {"path": {"o": "user_public"}},
                    }
                ],
                "emit_dtos": [
                    {
                        "emit": {"resource_path": ("platform", "auth", "users")},
                        "name": {"path": {"o": "create_user_body"}},
                    }
                ],
                "emit_enums": [
                    {
                        "emit": {"resource_path": ("platform", "auth", "users")},
                        "name": {"path": {"o": "user_status"}},
                    }
                ],
            },
            "features": [],
        },
    )

    assert (
        "export 'schemas/models/platform/auth/users/user_public/index.dart';" in output
    )
    assert (
        "export 'schemas/models/platform/auth/users/create_user_body/index.dart';"
        in output
    )
    assert "export 'schemas/enums/user_status/index.dart';" in output
    assert "schemas/platform/auth/users/enums" not in output
    assert "schemas/platform/auth/users/dtos" not in output


def test_dart_model_template_emits_json_key_for_renamed_fields(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "dart",
        relative_path=Path("{model}") / "model.dart.j2",
        context={
            "file": {"imports": []},
            "model": {
                "name": {"pascal": {"o": "CompanyPublic"}},
                "meta": {"has_extends": False, "super_fields": ()},
                "fields": [
                    {
                        "lang": {
                            "display_name": "defaultValue",
                            "type": "bool",
                            "required": True,
                            "json_key": "default",
                        },
                    },
                    {
                        "lang": {
                            "display_name": "name",
                            "type": "String",
                            "required": True,
                            "json_key": None,
                        },
                    },
                ],
            },
        },
    )

    assert "@JsonKey(name: 'default')" in output
    assert "final bool defaultValue;" in output
    assert "@JsonKey(name: 'name')" not in output
    assert "final String name;" in output


def test_next_version_barrel_keeps_server_only_modules_private(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{root}") / "[project.meta.api_version].ts.j2",
        context={"project": {"meta": {"api_version": "v1"}}},
    )

    assert "Do not export './api'" in output
    assert "Do not export './actions'" in output
    assert "export * from './routes';" in output
    assert "export * from './types';" in output
    assert "export * from './api';" not in output
    assert "export * from './actions';" not in output


def test_next_routes_template_renders_path_param_functions(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{root}") / "routes.ts.j2",
        context={
            "resources": [
                {
                    "name": {"camel": {"o": "companyMembers"}},
                    "operations": [
                        {
                            "lang": {
                                "function_name": "getCompanyMember",
                                "method": "get",
                            },
                            "api": {
                                "path": "/companies/{companyId}/members/{memberId}"
                            },
                            "meta": {
                                "has_path_params": True,
                                "path_params": ("companyId", "memberId"),
                            },
                        }
                    ],
                }
            ]
        },
    )

    assert "companyMembers" in output
    assert "getCompanyMember" in output
    assert "`/companies/${companyId}/members/${memberId}`" in output


def test_next_action_template_renders_multipart_action(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{resource}") / "[resource.name.path.o].actions.ts.j2",
        context={
            "file": {"imports": []},
            "resource": {
                "name": {
                    "path": {"o": "uploads"},
                    "camel": {"o": "uploads"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "UploadFile"}},
                        "lang": {"function_name": "uploadFile", "method": "post"},
                        "request_body": {"lang": {"required": True}},
                        "meta": {
                            "response_type": "UploadResponse",
                            "has_path_params": False,
                            "path_params": (),
                            "query_type": None,
                            "body_type": "UploadFileBody",
                            "is_multipart_request": True,
                        },
                    }
                ],
            },
        },
    )

    assert "body: FormData" in output
    assert "Uploads Server Actions" in output
    assert "requestOptions(" in output
    assert "): Promise<ApiBridgeResponse<UploadResponse>>" not in output
    assert "api.post<UploadResponse>(endpoint, input.body, options)" in output


def test_next_action_template_only_passes_query_when_query_type_exists(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{resource}") / "[resource.name.path.o].actions.ts.j2",
        context={
            "file": {"imports": []},
            "resource": {
                "name": {
                    "path": {"o": "availability"},
                    "camel": {"o": "availability"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "GetCompanyAvailability"}},
                        "lang": {
                            "function_name": "getCompanyAvailability",
                            "method": "get",
                        },
                        "request_body": None,
                        "meta": {
                            "response_type": "CompanyAvailabilityResponse",
                            "has_path_params": True,
                            "path_params": ("companyId",),
                            "query_type": "CompanyAvailabilityDetailQuery",
                            "body_type": None,
                            "is_multipart_request": False,
                        },
                    },
                    {
                        "name": {"pascal": {"o": "DeleteCompanyAvailability"}},
                        "lang": {
                            "function_name": "deleteCompanyAvailability",
                            "method": "delete",
                        },
                        "request_body": None,
                        "meta": {
                            "response_type": "CompanyAvailabilityDeletedResponse",
                            "has_path_params": True,
                            "path_params": ("companyId",),
                            "query_type": None,
                            "body_type": None,
                            "is_multipart_request": False,
                        },
                    },
                ],
            },
        },
    )

    assert "query?: CompanyAvailabilityDetailQuery;" in output
    assert "input?.query as Record<string, unknown>" in output
    assert output.count("input?.query as Record<string, unknown>") == 1
    assert "undefined,\n    false,\n  );" in output


def test_next_action_template_renders_ui_form_action_wrapper(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{resource}") / "[resource.name.path.o].actions.ts.j2",
        context={
            "file": {"imports": []},
            "resource": {
                "name": {
                    "path": {"o": "users"},
                    "camel": {"o": "users"},
                    "pascal": {"o": "Users"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "UpdateUser"}},
                        "lang": {
                            "function_name": "updateUser",
                            "method": "patch",
                        },
                        "request_body": {"lang": {"required": True}},
                        "meta": {
                            "response_type": "UserResponse",
                            "has_path_params": True,
                            "path_params": ("userId",),
                            "query_type": None,
                            "body_type": "UpdateUserBody",
                            "is_multipart_request": False,
                            "ui_enabled": True,
                            "ui_role": "update",
                        },
                    },
                ],
            },
        },
    )

    assert "import { redirect } from 'next/navigation';" in output
    assert "Users Server Actions" in output
    assert "UpdateUser Form Action" in output
    assert "type FormActionResult" in output
    assert "type UpdateUserActionResult = FormActionResult<" in output
    assert "export type UpdateUserActionResult" not in output
    assert "UpdateUserBody" in output
    assert "ApiBridgeResponse<UserResponse>" in output
    assert "export async function updateUserAction(" in output
    assert "): Promise<UpdateUserActionResult>" in output
    assert "const redirectPath = formActionRedirectPath(data);" in output
    assert "const body = cleanActionFormData<UpdateUserBody>(" in output
    assert "'__path:userId'" in output
    assert "params: {" in output
    assert "userId: actionFormDataValue(data, '__path:userId')" in output
    assert "const response = await updateUser({" in output
    assert "if (response.success && redirectPath)" in output
    assert "redirect(redirectPath);" in output
    assert "return { response, formdata: body };" in output


def test_next_action_helpers_use_reserved_form_control_fields(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{root}") / "actions" / "helpers.ts.j2",
        context={},
    )

    assert "const ACTION_REDIRECT_PATH_FIELD = '__redirect_path';" in output
    assert "Server Action Helpers" in output
    assert "'__delete'" in output
    assert "'__json_parse'" in output
    assert "'__boolean'" in output
    assert "'__number'" in output
    assert "'__date'" in output
    assert "data.get(ACTION_REDIRECT_PATH_FIELD)" in output
    assert "entryKey.startsWith(prefix)" in output
    assert "key.startsWith(ACTION_CONTROL_PREFIX)" in output


def test_next_action_template_renders_auth_form_action_with_standard_name(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{resource}") / "[resource.name.path.o].actions.ts.j2",
        context={
            "file": {"imports": []},
            "resource": {
                "name": {
                    "path": {"o": "auth"},
                    "camel": {"o": "auth"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "AdminLogin"}},
                        "lang": {
                            "function_name": "adminLogin",
                            "method": "post",
                        },
                        "request_body": {"lang": {"required": True}},
                        "meta": {
                            "response_type": "AuthSessionResponse",
                            "has_path_params": False,
                            "path_params": (),
                            "query_type": None,
                            "body_type": "AdminLoginBody",
                            "is_multipart_request": False,
                            "ui_enabled": True,
                            "ui_role": "auth",
                        },
                    },
                ],
            },
        },
    )

    assert "type AdminLoginActionResult = FormActionResult<" in output
    assert "export type AdminLoginActionResult" not in output
    assert "AdminLoginBody" in output
    assert "ApiBridgeResponse<AuthSessionResponse>" in output
    assert "export async function adminLoginAction(" in output
    assert "_prev: AdminLoginActionResult | null" in output
    assert "): Promise<AdminLoginActionResult>" in output
    assert "const response = await adminLogin({" in output


def test_next_resource_dto_barrel_exports_resource_dtos(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{resource_dto}") / "index.ts.j2",
        context={
            "resource": {
                "name": {"pascal": {"o": "Notifications"}},
                "dtos": [
                    {"name": {"path": {"o": "notification_list_response"}}},
                    {"name": {"path": {"o": "notification_partial"}}},
                ],
            }
        },
    )

    assert "export * from './notification_list_response';" in output
    assert "export * from './notification_partial';" in output


def test_next_enum_template_exports_options(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{enum}") / "[enum.name.path.o].ts.j2",
        context={
            "enum": {
                "name": {
                    "pascal": {"o": "UserStatus"},
                    "camel": {"o": "userStatus"},
                },
                "meta": {
                    "enum_values": (
                        {"safe_name": "active", "wire": "active"},
                        {"safe_name": "emailVerified", "wire": "emailVerified"},
                    )
                },
            }
        },
    )

    assert "export const userStatusOptions = [" in output
    assert "UserStatus" in output
    assert "Options list suitable for generated select fields" in output
    assert '{ label: enumLabel("active"), value: UserStatus.active }' in output
    assert (
        '{ label: enumLabel("emailVerified"), value: UserStatus.emailVerified }'
        in output
    )


def test_next_ui_columns_template_uses_list_item_schema(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_resource}") / "[resource.name.path.o]-columns.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {
                    "path": {"o": "users"},
                    "camel": {"o": "users"},
                    "pascal": {"o": "Users"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "UpdateUser"}},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "update",
                            "has_path_params": True,
                            "path_params": ("userId",),
                        },
                    },
                    {
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "list",
                            "ui_list_item_type": "UserPartial",
                            "ui_sort_fields": ("status",),
                            "ui_filter_fields": ("status",),
                        }
                    }
                ],
                "schemas": [
                    {
                        "name": {"pascal": {"o": "UserPartial"}},
                        "fields": [
                            {
                                "lang": {
                                    "display_name": "status",
                                    "type": "UserStatus",
                                    "sortable": True,
                                    "filterable": True,
                                },
                                "name": {"pascal": {"o": "Status"}},
                                "meta": {
                                    "enum_options": (
                                        {"wire": "active"},
                                        {"wire": "suspended"},
                                    )
                                },
                            },
                            {
                                "lang": {
                                    "display_name": "createdAt",
                                    "type": "Date",
                                    "sortable": True,
                                    "filterable": False,
                                },
                                "name": {"pascal": {"o": "CreatedAt"}},
                            },
                        ],
                    }
                ],
            }
        },
    )

    assert "Column<UserPartial>" in output
    assert "Users Table Columns" in output
    assert "from '@/gen/server/types/platform/users'" in output
    assert "key: 'status'" in output
    assert "const USERS_SORT_FIELDS: readonly string[]" in output
    assert "const USERS_FILTER_FIELDS: readonly string[]" in output
    assert "sortable: USERS_SORT_FIELDS.includes('status')" in output
    assert "filterable: USERS_FILTER_FIELDS.includes('status')" in output
    assert "function filterOption(" in output
    assert "filterOption('all', 'All Status', 'all')" in output
    assert "filterOption('active', enumLabel('active'), 'active')" in output
    assert "key: 'createdAt'" not in output
    assert "UsersActionsCell" in output
    assert "key: 'id'" in output
    assert "label: 'Actions'" in output


def test_next_ui_columns_template_hides_ids_objects_and_caps_fields(
    project_root: Path,
) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_resource}") / "[resource.name.path.o]-columns.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {
                    "path": {"o": "companies"},
                    "camel": {"o": "companies"},
                    "pascal": {"o": "Companies"},
                },
                "operations": [
                    {
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "list",
                            "ui_list_item_type": "CompanyPartial",
                            "ui_sort_fields": (),
                            "ui_filter_fields": (),
                        }
                    }
                ],
                "schemas": [
                    {
                        "name": {"pascal": {"o": "CompanyPartial"}},
                        "fields": [
                            {
                                "lang": {"display_name": "id", "type": "string"},
                                "name": {"pascal": {"o": "Id"}},
                            },
                            {
                                "lang": {"display_name": "companyId", "type": "string"},
                                "name": {"pascal": {"o": "CompanyId"}},
                            },
                            {
                                "lang": {"display_name": "location", "type": "GeoLocation"},
                                "name": {"pascal": {"o": "Location"}},
                            },
                            {
                                "lang": {"display_name": "status", "type": "CompanyStatus"},
                                "name": {"pascal": {"o": "Status"}},
                                "meta": {"enum_options": ({"wire": "active"},)},
                            },
                            {
                                "lang": {"display_name": "email", "type": "string"},
                                "name": {"pascal": {"o": "Email"}},
                            },
                            {
                                "lang": {"display_name": "name", "type": "string"},
                                "name": {"pascal": {"o": "Name"}},
                            },
                            {
                                "lang": {"display_name": "phone", "type": "string"},
                                "name": {"pascal": {"o": "Phone"}},
                            },
                            {
                                "lang": {"display_name": "paid", "type": "boolean"},
                                "name": {"pascal": {"o": "Paid"}},
                            },
                            {
                                "lang": {"display_name": "rating", "type": "number"},
                                "name": {"pascal": {"o": "Rating"}},
                            },
                            {
                                "lang": {"display_name": "startedAt", "type": "Date"},
                                "name": {"pascal": {"o": "StartedAt"}},
                            },
                            {
                                "lang": {"display_name": "extra", "type": "string"},
                                "name": {"pascal": {"o": "Extra"}},
                            },
                        ],
                    }
                ],
            }
        },
    )

    assert "key: 'id'" not in output
    assert "key: 'companyId'" not in output
    assert "key: 'location'" not in output
    assert "key: 'status'" in output
    assert "key: 'email'" in output
    assert "key: 'name'" in output
    assert "key: 'phone'" in output
    assert "key: 'paid'" in output
    assert "key: 'rating'" in output
    assert "key: 'startedAt'" not in output
    assert "key: 'extra'" not in output


def test_next_ui_table_template_wraps_core_data_table(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_resource}") / "[resource.name.path.o]-table.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {
                    "path": {"o": "users"},
                    "camel": {"o": "users"},
                    "pascal": {"o": "Users"},
                },
                "operations": [
                    {
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "list",
                            "ui_list_item_type": "UserPartial",
                        }
                    }
                ],
            }
        },
    )

    assert "import { DataTable } from '@/components/_core/data-table';" in output
    assert "Users Data Table" in output
    assert "fields?: UsersColumnVisibility;" in output
    assert "function visibleColumns(" in output
    assert "return fields[column.key as UsersColumnField] !== false;" in output
    assert "columns={visibleColumns(fields)}" in output


def test_next_ui_page_template_matches_core_table_page_shape(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_page}") / "page.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {
                    "path": {"o": "users"},
                    "camel": {"o": "users"},
                    "pascal": {"o": "Users"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "CreateUser"}},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "create",
                            "body_type": "CreateUserBody",
                            "has_path_params": False,
                            "path_params": (),
                        },
                    },
                    {
                        "lang": {"function_name": "listUsers"},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "list",
                            "ui_list_field": "users",
                            "ui_list_item_type": "UserPartial",
                            "has_path_params": False,
                            "path_params": (),
                            "query_type": "UserListQuery",
                        },
                    }
                ],
            }
        },
    )

    assert "import { Metadata } from 'next';" in output
    assert "Users Page" in output
    assert "import ReusableAppBar from '@/components/_core/reusable-appbar';" in output
    assert "import { DataTable } from '@/components/_core/data-table';" in output
    assert "import { TableFilters } from '@/components/_core/table-filters';" in output
    assert "import { CreateUserDialogButton }" in output
    assert "export const dynamic = 'force-dynamic';" in output
    assert "const resolvedSearchParams = await searchParams;" in output
    assert "query: resolvedSearchParams as UserListQuery" in output
    assert "columns={usersColumns}" in output
    assert "<CreateUserDialogButton" in output
    assert "data={data?.body?.users || []}" in output


def test_next_ui_dialog_template_wires_create_form_action(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_resource}") / "[resource.name.path.o]-dialogs.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {
                    "path": {"o": "users"},
                    "pascal": {"o": "Users"},
                },
                "operations": [
                    {
                        "name": {"pascal": {"o": "UpdateUser"}},
                        "lang": {"function_name": "updateUser"},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "update",
                            "body_type": "UpdateUserBody",
                            "has_path_params": True,
                            "path_params": ("userId",),
                        },
                    },
                    {
                        "name": {"pascal": {"o": "CreateUser"}},
                        "lang": {"function_name": "createUser"},
                        "docs": {"description": "Create a user"},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "create",
                            "body_type": "CreateUserBody",
                            "has_path_params": False,
                            "path_params": (),
                        },
                    }
                ],
            }
        },
    )

    assert "import {" in output
    assert "Users Dialogs And Row Actions" in output
    assert "createUserAction" in output
    assert "updateUserAction" in output
    assert "CreateUserFormFields" in output
    assert "UpdateUserFormFields" in output
    assert "useDialogAction(createUserAction" in output
    assert "defaultValue={row as Partial<UpdateUserBody>}" in output
    assert "<DialogFormShell" in output
    assert "action={action}" in output
    assert "export function CreateUserDialog" in output
    assert "export function CreateUserDialogButton" in output


def test_next_ui_form_template_renders_enum_select(project_root: Path) -> None:
    output = render_template(
        template_root=project_root / "templates" / "next",
        relative_path=Path("{ui_resource}") / "[resource.name.path.o]-form.tsx.j2",
        context={
            "resource": {
                "path": ("platform",),
                "name": {"path": {"o": "users"}},
                "operations": [
                    {
                        "name": {"pascal": {"o": "CreateUser"}},
                        "meta": {
                            "ui_enabled": True,
                            "ui_role": "create",
                            "body_type": "CreateUserBody",
                        },
                    }
                ],
                "schemas": [
                    {
                        "name": {"pascal": {"o": "CreateUserBody"}},
                        "fields": [
                            {
                                "api": {"required": True},
                                "lang": {
                                    "display_name": "status",
                                    "type": "UserStatus",
                                },
                                "name": {"pascal": {"o": "Status"}},
                                "meta": {
                                    "enum_options": (
                                        {"wire": "active"},
                                        {"wire": "emailVerified"},
                                    )
                                },
                            },
                            {
                                "api": {"required": False},
                                "lang": {
                                    "display_name": "roles",
                                    "type": "Array<UserRole>",
                                },
                                "name": {"pascal": {"o": "Roles"}},
                                "meta": {
                                    "enum_options": (
                                        {"wire": "admin"},
                                        {"wire": "company_owner"},
                                    )
                                },
                            },
                        ],
                    }
                ],
            }
        },
    )

    assert "from '@/components/ui/select';" in output
    assert "Form Fields" in output
    assert '<Select\n          name="status"' in output
    assert '<SelectItem value="active">{enumLabel(' in output
    assert '<SelectItem value="emailVerified">{enumLabel(' in output
    assert "import { useState } from 'react';" in output
    assert "function EnumArrayField(" in output
    assert '<EnumArrayField\n          name="roles"' in output
    assert "{ label: enumLabel('company_owner'), value: 'company_owner' }" in output
