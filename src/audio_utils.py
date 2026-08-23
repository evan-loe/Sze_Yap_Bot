import os
from pathlib import Path
from typing import Iterable, List
from pydub import AudioSegment


def _export_format_from_path(p: Path) -> str:
    suffix = p.suffix.lower().lstrip('.')
    return suffix if suffix else 'wav'


def normalize_file(src: str, target_dbfs: float = -12.0, out_dir: str | Path | None = None) -> str:
    """Normalize a single audio file to target dBFS and export to out_dir.

    Returns the path to the normalized file.
    """
    src_p = Path(src)
    if out_dir is None:
        out_dir = src_p.parent
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioSegment.from_file(src)
    # pydub reports dBFS; compute required gain
    try:
        change_in_dBFS = target_dbfs - audio.dBFS
    except Exception:
        change_in_dBFS = 0.0

    normalized = audio.apply_gain(change_in_dBFS)

    out_path = out_dir / src_p.name
    fmt = _export_format_from_path(src_p)
    normalized.export(out_path, format=fmt)
    return str(out_path)


def process_files(paths: Iterable[str], target_dbfs: float = -12.0, directory: str | Path | None = None) -> List[str]:
    """Normalize multiple files and return list of output paths.

    This mirrors the small surface used by the old `pynormalize.process_files` call.
    """
    out_paths: List[str] = []
    out_dir = Path(directory) if directory is not None else None
    for p in paths:
        out_paths.append(normalize_file(p, target_dbfs=target_dbfs, out_dir=out_dir))
    return out_paths
