import type { CompiledRelation } from '@/contract/index';
import type { EntityRelation } from '../../entities/entity.types';
import { cardinality, deleteBehavior } from '../shared/compiler-values';

export function compileRelation(relation: EntityRelation): CompiledRelation {
  const behavior = deleteBehavior(relation.onDelete);
  return {
    id: `relation:${relation.source}:${relation.name}`,
    key: relation.name,
    name: relation.name,
    sourceEntity: relation.source,
    targetEntity: relation.target.id,
    sourceField: relation.local,
    targetField: relation.foreign,
    cardinality: cardinality(relation.cardinality),
    required: relation.onDelete?.setNull !== true,
    ...(behavior ? { deleteBehavior: behavior } : {}),
  };
}
