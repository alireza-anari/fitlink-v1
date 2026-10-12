"""Independent byte/mode/tree proof of the exact completed C02 source."""

import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath

C02_COMMIT = "0905be6c6ca608d469fe33e87f514b22591132d1"
C02_TREE = "ed788191bb6f5011e6b35a63823ae8183af7b53d"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def object_hash(kind, body):
    return hashlib.sha1(
        kind.encode() + b" " + str(len(body)).encode() + b"\0" + body
    ).hexdigest()


def verify_baseline(root: Path) -> str:
    root = Path(root).absolute()
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe baseline root")
    if (root / ".git").exists():
        try:
            identity = subprocess.check_output(
                [
                    "git",
                    "--no-replace-objects",
                    "-c",
                    f"safe.directory={root}",
                    "-C",
                    str(root),
                    "rev-parse",
                    "HEAD",
                    "HEAD^{tree}",
                ],
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=10,
            ).splitlines()
        except (OSError, subprocess.SubprocessError) as error:
            raise ValueError("Unavailable baseline checkout identity") from error
        if identity != [C02_COMMIT, C02_TREE]:
            raise ValueError("Wrong baseline checkout ref")
    manifest = json.loads(
        Path(__file__).with_name("c03_source_manifest.json").read_text()
    )
    if (manifest["commit"], manifest["tree"]) != (C02_COMMIT, C02_TREE):
        raise ValueError("Incorrect baseline identity")
    entries = manifest["entries"]
    sources = {}
    directories = set()
    for entry in entries:
        path = PurePosixPath(entry["path"])
        if path.is_absolute() or ".." in path.parts or str(path) != entry["path"]:
            raise ValueError("Unsafe baseline manifest")
        if entry["type"] == "blob" and entry["mode"] in {"100644", "100755"}:
            if entry["path"] in sources:
                raise ValueError("Duplicate baseline source")
            sources[entry["path"]] = entry
        elif entry["type"] == "tree" and entry["mode"] == "040000":
            directories.add(entry["path"])
        else:
            raise ValueError("Unsupported baseline entry")
    for relative, entry in sources.items():
        path = root / relative
        if any(parent.is_symlink() for parent in (path, *path.parents)):
            raise ValueError("Unsafe baseline source")
        try:
            mode = path.stat().st_mode
            body = path.read_bytes()
        except OSError as error:
            raise ValueError("Missing baseline source") from error
        if not stat.S_ISREG(mode):
            raise ValueError("Invalid baseline source type")
        actual_mode = "100755" if mode & 0o111 else "100644"
        if actual_mode != entry["mode"] or object_hash("blob", body) != entry["sha"]:
            raise ValueError("Changed baseline source")
    # Only root-owned generated namespaces used by the immutable C02 runtime.
    generated_roots = {
        ".git",
        ".venv",
        "node_modules",
        "staticfiles",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "test-results",
        "playwright-report",
    }
    generated_files = {
        ".env.verify",
        ".env.c02-upgrade",
        ".runtime/upgrade/metadata.json",
    }
    for parent, children, files in os.walk(root, followlinks=False):
        for name in (*children, *files):
            path = Path(parent) / name
            relative = path.relative_to(root).as_posix()
            parts = PurePosixPath(relative).parts
            # Venv/node dependencies legitimately contain symlinks, but source
            # paths have already been checked independently above.
            if parts[0] in generated_roots:
                if relative == parts[0] and path.is_symlink():
                    raise ValueError("Unsafe baseline generated root")
                if name in children:
                    children.remove(name)
                continue
            if path.is_symlink():
                raise ValueError("Symlink in baseline")
            if relative == ".runtime/c01":
                from docker.c02_baseline import verify_baseline as verify_c01

                verify_c01(path)
                children.remove(name)
                continue
            if relative.startswith("static/dist/") or relative == "static/dist":
                if path.is_file() and not relative.endswith(".css"):
                    raise ValueError("Unexpected baseline build output")
                continue
            if "__pycache__" in parts:
                if path.is_file() and not relative.endswith(".pyc"):
                    raise ValueError("Unexpected baseline cache output")
                continue
            if relative in generated_files:
                if not path.is_file():
                    raise ValueError("Invalid baseline generated output")
                continue
            if path.is_file() and relative not in sources:
                raise ValueError("Unexpected baseline source")
            if (
                path.is_dir()
                and relative not in directories
                and relative
                not in {
                    ".runtime",
                    ".runtime/upgrade",
                }
            ):
                raise ValueError("Unexpected baseline directory")

    def tree(prefix=""):
        children = []
        for entry in entries:
            parent, _, name = entry["path"].rpartition("/")
            if parent == prefix:
                directory = entry["type"] == "tree"
                sha = tree(entry["path"]) if directory else entry["sha"]
                if directory and sha != entry["sha"]:
                    raise ValueError("Incorrect baseline subtree")
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

    if tree() != C02_TREE:
        raise ValueError("Incorrect baseline tree")
    return C02_TREE


if __name__ == "__main__":
    print("Verified immutable C02 source tree: " + verify_baseline(Path(sys.argv[1])))
