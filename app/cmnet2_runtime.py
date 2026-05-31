from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "ui_work"
OUTPUT_DIR = ROOT / "outputs"


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = env.get("CUDA_VISIBLE_DEVICES", "0")
    return env


def _clean_name(path: str | os.PathLike[str]) -> str:
    return Path(path).name.replace(" ", "_")


def _copy_file(source: str | os.PathLike[str], destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _prepare_refs(uploaded_refs: list[str] | None, ref_folder: str, job_dir: Path) -> Path:
    if uploaded_refs:
        refs_dir = job_dir / "refs"
        refs_dir.mkdir(parents=True, exist_ok=True)
        for index, ref in enumerate(uploaded_refs):
            suffix = Path(ref).suffix or ".jpg"
            _copy_file(ref, refs_dir / f"ref_{index:06d}{suffix}")
        return refs_dir

    if ref_folder and Path(ref_folder).exists():
        return Path(ref_folder)

    return ROOT / "assets" / "video_full" / "ref"


def _run_command(command: list[str]) -> tuple[int, str]:
    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        env=_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line)
    return proc.wait(), "".join(lines)


def status() -> str:
    weights = [
        ROOT / "weights" / "DINOv2FeatureV6_LocalAtten_s2_154000.pth",
        ROOT / "models" / "checkpoints" / "dinov2_vits14_pretrain.pth",
        ROOT / "models" / "checkpoints" / "resnet18-5c106cde.pth",
        ROOT / "models" / "checkpoints" / "resnet50-19c8e357.pth",
        ROOT / "models" / "facebookresearch_dinov2_main",
    ]
    present = sum(1 for path in weights if path.exists())
    cuda = "unknown"
    try:
        import torch

        if torch.cuda.is_available():
            cuda = f"{torch.cuda.get_device_name(0)} / CUDA {torch.version.cuda}"
        else:
            cuda = "not available"
    except Exception as exc:
        cuda = f"torch check failed: {exc}"

    return (
        f"CMNET2 root: {ROOT}\n"
        f"Model assets: {present}/{len(weights)} present\n"
        f"GPU: {cuda}\n"
        f"Outputs: {OUTPUT_DIR}"
    )


def colorize_image(input_image: str, reference_image: str, output_name: str) -> tuple[str | None, str]:
    if not input_image or not reference_image:
        return None, "Choose both a target image and a reference image."

    OUTPUT_DIR.mkdir(exist_ok=True)
    if not output_name:
        output_name = "cmnet2_image_output.jpg"
    if not Path(output_name).suffix:
        output_name += ".jpg"

    output_path = OUTPUT_DIR / _clean_name(output_name)
    command = [
        sys.executable,
        str(ROOT / "test_imge.py"),
        "--input",
        input_image,
        "--ref",
        reference_image,
        "--output",
        str(output_path),
    ]
    code, log = _run_command(command)
    if code != 0:
        return None, f"> {' '.join(command)}\n\n{log}\n[FAILED] Exit code {code}"
    return str(output_path), f"> {' '.join(command)}\n\n{log}\n[DONE] Wrote {output_path}"


def colorize_video(
    input_video: str,
    uploaded_refs: list[str] | None,
    ref_folder: str,
    output_name: str,
    max_side: int,
    window_size: int,
    top_k: int,
    mem_every: int,
) -> tuple[str | None, str]:
    if not input_video:
        return None, "Choose a target video."

    OUTPUT_DIR.mkdir(exist_ok=True)
    WORK_DIR.mkdir(exist_ok=True)
    job_dir = WORK_DIR / time.strftime("job_%Y%m%d_%H%M%S")
    job_dir.mkdir(parents=True, exist_ok=True)

    refs_dir = _prepare_refs(uploaded_refs, ref_folder, job_dir)
    if not refs_dir.exists():
        return None, f"Reference folder not found: {refs_dir}"

    if not output_name:
        output_name = "cmnet2_video_output.mp4"
    if not Path(output_name).suffix:
        output_name += ".mp4"

    output_path = OUTPUT_DIR / _clean_name(output_name)
    command = [
        sys.executable,
        str(ROOT / "test_video_full.py"),
        "--input",
        input_video,
        "--ref_path",
        str(refs_dir),
        "--output",
        str(output_path),
        "--max_side",
        str(max_side),
        "--window_size",
        str(window_size),
        "--top_k",
        str(top_k),
        "--mem_every",
        str(mem_every),
    ]
    code, log = _run_command(command)
    if code != 0:
        return None, f"> {' '.join(command)}\n\n{log}\n[FAILED] Exit code {code}"
    return str(output_path), f"> {' '.join(command)}\n\n{log}\n[DONE] Wrote {output_path}"
