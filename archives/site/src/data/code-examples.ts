import type { CodeExample } from "./types";

export const ENTITY_CODE: CodeExample = {
  filename: "user.entity.config.ts",
  language: "typescript",
  code: `export default class UserEntityConfig
   implements EntityConfigBase {
  key = "user";

  fields = this.defineFields({
    email: stringField({
      length: 255,
    }),

    status: enumField([
      "active",
      "suspended",
    ]),
  });
}`,
};

export const TEMPLATE_CODE: CodeExample = {
  filename: "dto.create.codepurify",
  language: "codepurify",
  code: `type I{{entity.name.casing.pascal}} = {

  // Each field becomes a property

  };

class {{entity.name.casing.pascal}}Repo{

  async create(dto: I{|...pascal|}) {
    return this.create(dto);
  }
  ...more methods
};

`,
};

export const OUTPUT_CODE: CodeExample = {
  filename: "create-user.dto.ts",
  language: "typescript",
  code: `export type IUser = {
  email: string;
  status: UserStatus;

  // ...other fields
};

class UseryRepo {
  constructor() {}

  async create(dto: IUser) {
    return this.create(dto);
  }

}
`,
};
