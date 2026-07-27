from __future__ import annotations

from codepotg_author import Author


def main() -> int:
    author = Author("manual-connected-project")
    author.group("Accounts")
    author.schema(
        "User",
        {
            "id": str,
            "email": str,
            "is_active": bool,
        },
    )

    print(f"author session: {author.author_id}")
    print(f"declarations: {len(author.declarations)}")
    for declaration in author.declarations:
        print(f"  {declaration.kind.value}: {declaration.id}")

    compile_method = getattr(author, "compile", None)
    if callable(compile_method):
        print("codepotg-author now exposes compile(); update this manual probe to test the full path")
        return 1

    print("EXPECTED CURRENT GAP: codepotg-author can declare typed refs but cannot compile a Contract yet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
