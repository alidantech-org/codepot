import { ECOSYSTEM } from "@/generated/docs";

export interface EcosystemLink {
  kind: string;
  label: string;
  url: string | null;
  status: "available" | "tbd";
}

export interface EcosystemProduct {
  id: string;
  name: string;
  kind: string;
  stage: string;
  status: string;
  availability: string;
  docsSlug: string;
  description: string;
  role: string;
  install: string | null;
  command: string | null;
  links: EcosystemLink[];
}

export interface EcosystemStage {
  id: string;
  title: string;
  summary: string;
  products: string[];
}

export interface EcosystemConfig {
  project: {
    name: string;
    tagline: string;
    description: string;
    github: string;
    license: string;
  };
  stages: EcosystemStage[];
  products: EcosystemProduct[];
}

export type AvailableEcosystemLink = EcosystemLink & { status: "available"; url: string };

export const ecosystem = ECOSYSTEM as unknown as EcosystemConfig;

export function getProductById(id: string): EcosystemProduct | undefined {
  return ecosystem.products.find((product) => product.id === id);
}

export function getProductsForStage(stageId: string): EcosystemProduct[] {
  const stage = ecosystem.stages.find((candidate) => candidate.id === stageId);
  if (!stage) return [];
  return stage.products.flatMap((productId) => {
    const product = getProductById(productId);
    return product ? [product] : [];
  });
}

export function getAvailableLinks(product: EcosystemProduct): AvailableEcosystemLink[] {
  return product.links.filter(
    (link): link is AvailableEcosystemLink =>
      link.status === "available" && typeof link.url === "string",
  );
}
