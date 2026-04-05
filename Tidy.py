#!/usr/bin/env python3
"""
tidy — scan a folder and sort files into categorized subfolders.
"""

import shutil
import argparse
import sys
from pathlib import Path
from collections import defaultdict

# Maps subfolder names to the file extensions that belong in them.
# First match wins when an extension appears in multiple categories.
CATEGORIES: dict[str, list[str]] = {
    "Images":       [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
                     ".webp", ".svg", ".ico", ".heic", ".heif", ".raw",
                     ".cr2", ".nef", ".arw"],
    "Videos":       [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                     ".m4v", ".mpg", ".mpeg", ".3gp", ".ts", ".vob"],
    "Audio":        [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a",
                     ".opus", ".aiff", ".mid", ".midi"],
    "Documents":    [".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md",
                     ".csv", ".xls", ".xlsx", ".ods", ".ppt", ".pptx",
                     ".odp", ".epub", ".mobi"],
    "Archives":     [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz",
                     ".lz", ".lzma", ".zst", ".cab", ".iso", ".dmg"],
    "Executables":  [".exe", ".msi", ".bat", ".cmd", ".ps1", ".sh", ".bash",
                     ".app", ".deb", ".rpm", ".apk", ".bin", ".run"],
    "Code":         [".py", ".js", ".ts", ".html", ".css", ".java", ".c",
                     ".cpp", ".cs", ".go", ".rs", ".php", ".rb", ".swift",
                     ".kt", ".r", ".sql", ".json", ".xml", ".yaml", ".yml",
                     ".toml", ".ini", ".cfg", ".env"],
    "Fonts":        [".ttf", ".otf", ".woff", ".woff2", ".eot"],
    "Ebooks":       [".epub", ".mobi", ".azw", ".azw3", ".fb2"],
    "3D_Models":    [".obj", ".fbx", ".stl", ".blend", ".dae", ".3ds", ".gltf",
                     ".glb"],
    "Torrents":     [".torrent"],
    "Disk_Images":  [".iso", ".img", ".vhd", ".vhdx", ".vmdk"],
}

MISC_FOLDER = "Miscellaneous"  # destination for unrecognized extensions

_MAX_COPIES = 9_999  # upper limit for duplicate filename attempts


def _build_ext_map(categories: dict[str, list[str]]) -> dict[str, str]:
    """Flatten CATEGORIES into a single extension -> folder lookup."""
    ext_map: dict[str, str] = {}
    for folder, exts in categories.items():
        for ext in exts:
            ext_map.setdefault(ext, folder)
    return ext_map


_EXT_MAP = _build_ext_map(CATEGORIES)


# Use colours only when stdout is a real terminal
_COLOR = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class C:
    RESET  = "\033[0m"  if _COLOR else ""
    BOLD   = "\033[1m"  if _COLOR else ""
    DIM    = "\033[2m"  if _COLOR else ""
    RED    = "\033[91m" if _COLOR else ""
    GREEN  = "\033[92m" if _COLOR else ""
    YELLOW = "\033[93m" if _COLOR else ""
    BLUE   = "\033[94m" if _COLOR else ""
    CYAN   = "\033[96m" if _COLOR else ""


def _div(label: str = "") -> None:
    """Print a divider line, with an optional centred label."""
    line = "─" * 60
    if label:
        pad = (58 - len(label)) // 2
        line = "─" * pad + f" {label} " + "─" * (58 - pad - len(label))
    print(f"{C.BOLD}{C.CYAN}{line}{C.RESET}")


def categorize(file: Path) -> str:
    """Return the folder name for a file based on its extension."""
    return _EXT_MAP.get(file.suffix.lower(), MISC_FOLDER)


def unique_dest(dest: Path) -> Path:
    """Return dest, or a numbered variant if the path already exists.

    e.g. photo.jpg → photo (1).jpg → photo (2).jpg …
    """
    if not dest.exists():
        return dest
    stem, suffix, parent = dest.stem, dest.suffix, dest.parent
    for n in range(1, _MAX_COPIES + 1):
        candidate = parent / f"{stem} ({n}){suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError(
        f"Could not find a free filename after {_MAX_COPIES} tries: {dest.name}"
    )


def organize(
    source_dir: str,
    dry_run: bool = False,
    recursive: bool = False,
    skip_hidden: bool = True,
    verbose: bool = True,
) -> dict[str, int]:
    """Scan source_dir and move files into categorized subfolders.

    Args:
        source_dir:   Path to the directory to organize.
        dry_run:      If True, print what would happen but don't touch anything.
        recursive:    If True, also scan subdirectories.
        skip_hidden:  If True (default), skip files whose name starts with '.'.
        verbose:      If True (default), print each file as it is processed.

    Returns:
        dict[str, int]: category name -> number of files moved.

    Raises:
        FileNotFoundError: if source_dir does not exist.
        NotADirectoryError: if source_dir is not a directory.
    """
    source = Path(source_dir).expanduser().resolve()

    if not source.exists():
        raise FileNotFoundError(f"Directory not found: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Not a directory: {source}")

    # Header
    print()
    _div()
    print(f"{C.BOLD}  📂  py-tidy{C.RESET}")
    print(f"{C.DIM}  Source : {source}{C.RESET}")
    mode_label = f"{C.YELLOW}DRY RUN{C.RESET}{C.DIM} — no files will be moved" if dry_run else f"{C.GREEN}LIVE{C.RESET}"
    print(f"{C.DIM}  Mode   : {C.RESET}{mode_label}")
    _div()
    print()

    # Collect files (recursively or top-level only)
    if recursive:
        all_files = [p for p in source.rglob("*") if p.is_file()]
    else:
        all_files = [p for p in source.iterdir() if p.is_file()]

    if skip_hidden:
        all_files = [f for f in all_files if not f.name.startswith(".")]

    # Skip the script itself if it lives in the target folder
    script_path = Path(__file__).resolve()
    all_files = [f for f in all_files if f.resolve() != script_path]

    if not all_files:
        print(f"{C.YELLOW}  No files found to organize.{C.RESET}\n")
        return {}

    stats: dict[str, int] = defaultdict(int)
    errors: list[str] = []

    for file in sorted(all_files, key=lambda p: p.name.lower()):
        category  = categorize(file)
        dest_folder = source / category
        dest_file   = unique_dest(dest_folder / file.name)

        if verbose:
            action_tag = f"{C.GREEN}  MOVE{C.RESET}" if not dry_run else f"{C.YELLOW}  SKIP{C.RESET}"
            rel = file.relative_to(source) if file.is_relative_to(source) else file
            print(
                f"  {action_tag}  "
                f"{C.DIM}{str(rel):<45}{C.RESET}  {C.DIM}→{C.RESET}  "
                f"{C.BLUE}{category}/{C.RESET}{dest_file.name}"
            )

        if not dry_run:
            try:
                dest_folder.mkdir(parents=True, exist_ok=True)
                shutil.move(file, dest_file)
                stats[category] += 1
            except Exception as exc:
                errors.append(f"{file.name}: {exc}")
                print(f"  {C.RED}  ERR   {C.RESET}{file.name}: {exc}")
        else:
            stats[category] += 1

    # Summary
    total = sum(stats.values())
    print()
    _div("summary")

    if stats:
        max_count = max(stats.values())
        for cat, count in sorted(stats.items(), key=lambda x: -x[1]):
            bar_len = round(count / max_count * 24) if max_count else 0
            bar = f"{C.CYAN}{'█' * bar_len}{C.DIM}{'░' * (24 - bar_len)}{C.RESET}"
            print(f"  {C.BLUE}{cat:<18}{C.RESET}  {bar}  {C.BOLD}{count}{C.RESET}")
        print()

    verb = "moved" if not dry_run else "would be moved"
    status_color = C.GREEN if not errors else C.YELLOW
    print(
        f"  {status_color}{C.BOLD}{total}{C.RESET} file(s) {verb}  "
        f"{C.DIM}|{C.RESET}  "
        f"{C.RED if errors else C.DIM}{len(errors)} error(s){C.RESET}"
    )

    if errors:
        print(f"\n{C.RED}  Errors:{C.RESET}")
        for e in errors:
            print(f"    {C.DIM}•{C.RESET} {e}")

    _div()
    print()

    return dict(stats)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="tidy",
        description="Sort files in a folder into categorized subfolders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python tidy.py                          organize current directory
  python tidy.py ~/Downloads              organize Downloads
  python tidy.py ~/Downloads --dry-run    preview without moving
  python tidy.py . -r -q                 recursive, summary only
  python tidy.py --list-categories        show all supported types
        """,
    )
    p.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="directory to organize (default: current directory)",
    )
    p.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="preview what would happen without moving any files",
    )
    p.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="also scan subdirectories; files are always moved to category "
             "folders in the root of the target directory",
    )
    p.add_argument(
        "--include-hidden",
        action="store_true",
        help="include hidden files (those starting with a dot)",
    )
    p.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="only show the summary, not individual file moves",
    )
    p.add_argument(
        "--list-categories",
        action="store_true",
        help="print all supported categories and extensions, then exit",
    )
    return p


def print_categories() -> None:
    """Print every category and its associated extensions."""
    print()
    _div("supported categories")
    for folder, exts in CATEGORIES.items():
        shown  = "  ".join(exts[:8])
        more   = f"  {C.DIM}+{len(exts) - 8} more{C.RESET}" if len(exts) > 8 else ""
        print(f"  {C.BLUE}{folder:<18}{C.RESET} {C.DIM}{shown}{more}{C.RESET}")
    print(f"  {C.YELLOW}{MISC_FOLDER:<18}{C.RESET} {C.DIM}(everything else){C.RESET}")
    _div()
    print()


def main() -> None:
    parser = build_parser()
    args   = parser.parse_args()

    if args.list_categories:
        print_categories()
        return

    try:
        organize(
            source_dir=args.directory,
            dry_run=args.dry_run,
            recursive=args.recursive,
            skip_hidden=not args.include_hidden,
            verbose=not args.quiet,
        )
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"\n{C.RED}  ✗ {exc}{C.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()