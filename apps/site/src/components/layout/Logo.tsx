import Link from "next/link";
import Image from "next/image";

export default function Logo() {
  return (
    <Link
      href="/"
      className="group flex min-w-0 items-center"
      aria-label="Codepot home"
    >
      <Image
        src="/logo.svg"
        alt=""
        width={24}
        height={30}
        priority
        className="h-12 mb-3.5 w-auto mr-1 shrink-0 transition-transform duration-300 group-hover:-rotate-3 motion-reduce:transition-none"
      />
      <span className="landing-display truncate text-2xl font-semibold tracking-tight text-foreground transition-colors group-hover:text-primary">
        <code className="font-mono font-bold">Code</code><span className="text-primary uppercase">Pot</span>
      </span>
    </Link>
  );
}
