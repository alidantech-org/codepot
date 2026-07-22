import { paths, file } from 'codepurify';
import { defineCodepurifyTemplates } from 'codepurify';

export default defineCodepurifyTemplates({
  rootDir: '__CODEPURIFY_TEMPLATE_ROOT_DIR__',
  templates: [
    // ============================================================================
    // ENTITY TEMPLATES (Core entity definitions)
    // ============================================================================

    {
      name: 'constants',
      templatePath: './code/constants/constants.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.constants').ext('ts'),
      description: 'Creates entity constants.',
      type: 'entity',
    },

    {
      name: 'entity',
      templatePath: './code/entity.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.entity').ext('ts'),
      description: 'Creates a TypeORM entity.',
      type: 'entity',
    },

    {
      name: 'schema.entity',
      templatePath: './code/schema/entity.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.schema').ext('ts'),
      description: 'Creates an entity schema.',
      type: 'entity',
    },

    {
      name: 'dto.create',
      templatePath: './code/dto.create.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab, 'dto'],
      fileName: file(paths.entity.name.kebab).prefix('create-').suffix('.dto').ext('ts'),
      description: 'Creates a create DTO.',
      type: 'entity',
    },

    {
      name: 'dto.update',
      templatePath: './code/dto.update.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab, 'dto'],
      fileName: file(paths.entity.name.kebab).prefix('update-').suffix('.dto').ext('ts'),
      description: 'Creates an update DTO.',
      type: 'entity',
    },

    {
      name: 'types.context',
      templatePath: './code/types/context.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.types').ext('ts'),
      description: 'Creates type context.',
      type: 'entity',
    },

    // ============================================================================
    // RESOURCE TEMPLATES (Supporting resources and utilities)
    // ============================================================================

    {
      name: 'controller',
      templatePath: './code/controller.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.controller').ext('ts'),
      description: 'Creates a NestJS controller.',
      type: 'resource',
    },

    {
      name: 'repository',
      templatePath: './code/repository.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.repository').ext('ts'),
      description: 'Creates a TypeORM repository.',
      type: 'resource',
    },

    {
      name: 'service',
      templatePath: './code/service.ts.codepurify',
      outputFolder: [paths.entity.groupKey, paths.entity.name.kebab],
      fileName: file(paths.entity.name.kebab).suffix('.service').ext('ts'),
      description: 'Creates a service.',
      type: 'resource',
    },
  ],
});
