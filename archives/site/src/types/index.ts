export interface Feature {
  label: string;
  color: "blue" | "purple" | "teal";
}

export interface PipelineStep {
  step: string;
  description: string;
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

export interface DotProps {
  color: "blue" | "purple" | "teal";
}

export interface CodeBlockProps {
  example: CodeExample;
}
