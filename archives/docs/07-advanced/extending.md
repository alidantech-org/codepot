---
title: Extending the Language
description: Adding custom syntax and helpers to Codepurify
---

# Extending the Language

Add custom syntax, helpers, and functions to Codepurify templates.

## Custom Helpers

```typescript
import { HelperRegistry } from "@codepurify/core";

class CustomHelpers {
  static formatDate(date: string): string {
    return new Date(date).toISOString().split("T")[0];
  }

  static pluralize(count: number, word: string): string {
    return count === 1 ? word : `${word}s`;
  }

  static toEnum(items: string[]): string {
    return items
      .map((item) => `  ${item.toUpperCase()} = '${item}'`)
      .join(",\n");
  }
}
```

## Helper Registration

```typescript
const registry = new HelperRegistry();
registry.register("formatDate", CustomHelpers.formatDate);
registry.register("pluralize", CustomHelpers.pluralize);
registry.register("toEnum", CustomHelpers.toEnum);
```

## Template Usage

```codepurify
{| formatDate(entity.created_at) |} {| pluralize(field.count, 'item') |} export
enum {| entity.names.casing.pascal |}Enum { {|
toEnum(entity.fields.arrays.all.items.map(item => item.names.original)) |} }
```

## Custom Block Helpers

```typescript
class BlockHelpers {
  static conditionalRender(context: any, options: any): string {
    const condition = options.hash.condition;
    const content = options.fn(context);

    if (this.evaluateCondition(condition)) {
      return content;
    }
    return "";
  }
}
```

## Syntax Extensions

```typescript
class CustomParser {
  parseCustomSyntax(template: string): ParsedTemplate {
    // Parse custom {|custom ...|} syntax
    const customRegex = /\{|custom\s+(.+?)\s*!\}/g;

    return template.replace(customRegex, (match, expression) => {
      return this.evaluateCustomExpression(expression);
    });
  }

  private evaluateCustomExpression(expr: string): string {
    // Custom expression evaluation logic
    return `/* Custom: ${expr} */`;
  }
}
```

## Plugin System

```typescript
interface CodepurifyPlugin {
  name: string;
  version: string;
  helpers?: Record<string, Function>;
  parsers?: Parser[];
  middleware?: Middleware[];
}

class EnumPlugin implements CodepurifyPlugin {
  name = "enum-generator";
  version = "1.0.0";

  helpers = {
    toEnum: CustomHelpers.toEnum,
    enumValue: this.generateEnumValue,
  };

  private generateEnumValue(name: string): string {
    return name.toUpperCase().replace(/[^A-Z0-9]/g, "_");
  }
}
```

## Plugin Registration

```typescript
import { Codepurify } from "@codepurify/core";

const app = new Codepurify();
app.use(new EnumPlugin());
```
