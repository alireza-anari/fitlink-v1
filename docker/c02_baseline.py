"""Verify immutable C01 source bytes before any rehearsal uses the fixture."""

import hashlib
import json
import sys
from pathlib import Path

C01_COMMIT = "75c551e5b9bbbfb7777ee52b09a1993b681e921a"
C01_TREE = "4dff1ebd5a32ed0359552bf29012d9d1ecf09b24"


def object_hash(kind, body):
    return hashlib.sha1(
        kind.encode() + b" " + str(len(body)).encode() + b"\0" + body
    ).hexdigest()


def verify_baseline(root: Path) -> str:
    manifest = json.loads(
        Path(__file__).with_name("c01_source_manifest.json").read_text()
    )
    if (manifest["commit"], manifest["tree"]) != (C01_COMMIT, C01_TREE):
        raise ValueError("Invalid baseline identity")
    entries = manifest["entries"]
    sources = {e["path"] for e in entries if e["type"] == "blob"}
    generated = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        "staticfiles",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "test-results",
        "playwright-report",
    }
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in generated for part in relative.parts):
            continue
        if relative.parts[:2] == ("static", "dist") or str(relative) == ".env.verify":
            continue
        if path.is_symlink() or (path.is_file() and str(relative) not in sources):
            raise ValueError("Unexpected baseline source")
    for entry in entries:
        if entry["type"] != "blob":
            continue
        path = root / entry["path"]
        if (
            not path.is_file()
            or path.is_symlink()
            or any(p.is_symlink() for p in path.parents)
        ):
            raise ValueError("Missing or unsafe baseline source")
        body = path.read_bytes()
        actual_mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        if object_hash("blob", body) != entry["sha"] or actual_mode != entry["mode"]:
            raise ValueError("Changed baseline source")

    def tree(prefix=""):
        children = []
        for entry in entries:
            parent = entry["path"].rsplit("/", 1)[0] if "/" in entry["path"] else ""
            if parent == prefix:
                name = entry["path"].rsplit("/", 1)[-1]
                directory = entry["type"] == "tree"
                sha = tree(entry["path"]) if directory else entry["sha"]
                children.append(
                    (
                        name + ("/" if directory else ""),
                        entry["mode"].lstrip("0"),
                        name,
                        sha,
                    )
                )
        body = b"".join(
            mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(sha)
            for _, mode, name, sha in sorted(children)
        )
        return object_hash("tree", body)

    if tree() != C01_TREE:
        raise ValueError("Incorrect baseline tree")
    return C01_TREE


if __name__ == "__main__":
    print(
        "Verified immutable C01 source tree: "
        + verify_baseline(Path(sys.argv[1]).resolve())
    )
