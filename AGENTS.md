# GGF CMNET2 Agent Notes

This repository is the public source for the GGF Windows/NVIDIA standalone CMNET2 colorization app.

## What This App Does

- It colorizes grayscale images and videos using CMNET2 / ColorMNet.
- It needs an NVIDIA CUDA GPU for practical use.
- It provides a Gradio browser UI in `app/app.py`.
- It writes generated files to `outputs/`.

## Member Installation Handoff

The member-facing AI-agent installation guide is:

`AGENT-INSTALL-GGF-CMNET2.txt`

That file is meant to be given to another AI agent. It should install the app for the user, not create an installer product. Keep it aligned with the Get Going Fast Agentic Install v2 style: disclaimer acknowledgement, workspace/drive choice, environment-first checks, app-local dependency installs, model verification, breadcrumb log, and honest failure reporting.

## Packaging Contract

- Do not commit model files, weights, `.venv`, outputs, generated videos, or zip files.
- Keep the public repo clone folder named `GGF-CMNET2`.
- Use app-local `.venv` only.
- Keep the GGF launch pattern simple: a parent folder with `CLICK-ME-TO-RUN.bat` and `START-HERE.txt`.
- Validate with a CUDA status check and at least one image smoke test when changing install or runtime behavior.

## Maintenance Notes

- Keep UI changes in `app/app.py`.
- Keep runtime behavior in `app/cmnet2_runtime.py`.
- Keep Windows console output ASCII-safe.
- Preserve the local PyTorch attention fallback so Windows installs do not require compiling `spatial_correlation_sampler`.
