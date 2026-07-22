export interface Feature {
  label: string;
  color: "blue" | "purple" | "teal";
}

export interface PipelineStep {
  step: string;
  description: string;
  details: string;
  icon?: string;
}

export interface UseCase {
  title: string;
  items: string[];
}

export interface CodeExample {
  filename: string;
  language: string;
  code: string;
}
