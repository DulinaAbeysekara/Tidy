# 🗂️ Tidy

A simple command-line tool that scans a folder and automatically sorts files into categorized subfolders — no configuration needed.

## 🚀 Quick Start

1. Download `tidy.py` and place it anywhere on your system
2. Open a terminal and navigate to the folder you want to organize
3. Run:
```bash
   python tidy.py
```
   That's it — your files will be sorted into subfolders automatically.

> Tip: Use `--dry-run` first to preview what will move before committing.

## ✨ Features

- Sorts files into **12 categories** (Images, Videos, Audio, Documents, Archives, and more)
- **Dry-run mode** — preview what will happen before moving anything
- **Recursive mode** — optionally scan subdirectories
- **Collision-safe** — auto-renames duplicates (e.g. `photo (1).jpg`)
- Skips hidden files by default
- Won't move itself if it lives in the target folder
- Coloured terminal output with a summary bar chart

## 📦 Requirements

- Python **3.9+**
- No third-party dependencies — standard library only

## 🚀 Usage

```bash
# Organize the current directory
python tidy.py

# Organize a specific folder
python tidy.py ~/Downloads

# Preview without moving anything
python tidy.py ~/Downloads --dry-run

# Recursive scan, summary only
python tidy.py . -r -q

# Include hidden files
python tidy.py ~/Downloads --include-hidden

# List all supported categories and extensions
python tidy.py --list-categories
```

## 🗂️ Categories

| Folder | File types |
|---|---|
| `Images` | `.jpg` `.jpeg` `.png` `.gif` `.webp` `.svg` `.heic` `.raw` … |
| `Videos` | `.mp4` `.mkv` `.avi` `.mov` `.wmv` `.webm` … |
| `Audio` | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.m4a` … |
| `Documents` | `.pdf` `.docx` `.txt` `.md` `.csv` `.xlsx` `.pptx` … |
| `Archives` | `.zip` `.rar` `.7z` `.tar` `.gz` `.dmg` … |
| `Executables` | `.exe` `.msi` `.sh` `.bat` `.apk` `.deb` … |
| `Code` | `.py` `.js` `.ts` `.html` `.css` `.json` `.yaml` … |
| `Fonts` | `.ttf` `.otf` `.woff` `.woff2` |
| `Ebooks` | `.epub` `.mobi` `.azw` `.fb2` |
| `3D_Models` | `.obj` `.fbx` `.stl` `.blend` `.gltf` |
| `Torrents` | `.torrent` |
| `Disk_Images` | `.iso` `.img` `.vhd` `.vmdk` |
| `Miscellaneous` | anything else |

> Run `python tidy.py --list-categories` to see the full list at any time.

## ⚙️ Options

| Flag | Short | Description |
|---|---|---|
| `--dry-run` | `-n` | Preview moves without touching any files |
| `--recursive` | `-r` | Also scan subdirectories |
| `--include-hidden` | | Include files starting with `.` |
| `--quiet` | `-q` | Show summary only, not individual file moves |
| `--list-categories` | | Print all categories and extensions, then exit |

## 📋 Example Output

```
────────────────────────────────────────────────────────────
  📂  py-tidy
  Source : /home/user/Downloads
  Mode   : LIVE
────────────────────────────────────────────────────────────

  MOVE  resume.pdf                                  →  Documents/resume.pdf
  MOVE  photo.heic                                  →  Images/photo.heic
  MOVE  archive.zip                                 →  Archives/archive.zip

────────────────── summary ─────────────────────────────────
  Documents           ████████░░░░░░░░░░░░░░░░  3
  Images              ████████████████░░░░░░░░  6
  Archives            ████░░░░░░░░░░░░░░░░░░░░  1

  10 file(s) moved  |  0 error(s)
────────────────────────────────────────────────────────────
```

## 📝 Notes

- When two files share the same name in the same category folder, the newer one is renamed automatically (e.g. `report (1).pdf`) — nothing is ever overwritten.
- Files already inside a category subfolder are left untouched when running non-recursively.
- Extension conflicts (e.g. `.epub` appears in both Documents and Ebooks) are resolved by **first definition wins** — see `CATEGORIES` in the source to adjust priority.
