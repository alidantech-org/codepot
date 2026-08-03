import type { DotProps } from "@/types";

export function Dot({ color }: DotProps) {
  const map: Record<DotProps["color"], string> = {
    blue: "bg-blue-500",
    purple: "bg-purple-500",
    teal: "bg-teal-500",
  };
  return (
    <span
      className={`mt-[5px] h-1.5 w-1.5 shrink-0 rounded-full ${map[color]}`}
    />
  );
}
