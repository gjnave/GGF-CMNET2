from __future__ import annotations

import argparse
import os
from pathlib import Path

import gradio as gr

from cmnet2_runtime import colorize_image, colorize_video, status


ROOT = Path(__file__).resolve().parents[1]

CSS = """
:root {
    --ggf-ink: #14120f;
    --ggf-paper: #fff9ed;
    --ggf-cream: #f4ead7;
    --ggf-red: #d83b2a;
    --ggf-blue: #174c62;
    --ggf-gold: #d99b2b;
    --ggf-line: #d8d0c3;
    --ggf-muted: #665f52;
}
body, .gradio-container {
    background:
        linear-gradient(135deg, rgba(216, 59, 42, 0.07), transparent 34%),
        linear-gradient(315deg, rgba(23, 76, 98, 0.12), transparent 42%),
        #fbf6eb !important;
    color: var(--ggf-ink);
    font-family: "Segoe UI", Arial, sans-serif;
}
.gradio-container {
    max-width: 1260px !important;
}
.brand-hero {
    border: 1px solid rgba(20, 18, 15, 0.12);
    border-radius: 8px;
    padding: 26px 30px;
    background:
        linear-gradient(120deg, rgba(20, 18, 15, 0.94), rgba(23, 76, 98, 0.9)),
        repeating-linear-gradient(90deg, rgba(255,255,255,0.07) 0, rgba(255,255,255,0.07) 1px, transparent 1px, transparent 18px);
    color: #fff8ec;
    box-shadow: 0 18px 44px rgba(20, 18, 15, 0.16);
}
.brand-lockup {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
}
.brand-badge {
    display: inline-flex;
    width: 44px;
    height: 44px;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: var(--ggf-red);
    color: #fff8ec;
    font-weight: 900;
    box-shadow: inset 0 -4px 0 rgba(0, 0, 0, 0.18);
}
.brand-kicker {
    color: #f5c35d;
    font-weight: 800;
    margin: 0;
}
.brand-hero h1 {
    margin: 0;
    font-size: 40px;
    line-height: 1.02;
    color: #fff8ec !important;
}
.brand-copy {
    max-width: 840px;
    color: #f4ead7;
    font-size: 16px;
    margin: 14px 0 12px;
}
.brand-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}
.brand-chip {
    border: 1px solid rgba(255, 248, 236, 0.22);
    border-radius: 999px;
    padding: 6px 10px;
    color: #fff8ec;
    background: rgba(255, 248, 236, 0.08);
    font-size: 13px;
}
.panel {
    border: 1px solid var(--ggf-line);
    border-radius: 8px;
    padding: 16px;
    background: rgba(255, 252, 245, 0.9);
}
.run-button button, .run-button, button.primary, .gradio-button.primary {
    background: linear-gradient(180deg, #e24a38, var(--ggf-red)) !important;
    border-color: #b92f22 !important;
    color: #fff8ec !important;
    font-weight: 900 !important;
    box-shadow: 0 12px 22px rgba(216, 59, 42, 0.22) !important;
}
.utility-button button, .utility-button {
    border: 1px solid #cfc3af !important;
    background: #fffaf0 !important;
    color: var(--ggf-ink) !important;
    font-weight: 800 !important;
}
.status-box textarea {
    font-family: Consolas, monospace !important;
    font-size: 12px !important;
}
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(title="GGF CMNET2", analytics_enabled=False) as app:
        gr.HTML(
            "<div class='brand-hero'>"
            "<div class='brand-lockup'><div class='brand-badge'>GGF</div>"
            "<p class='brand-kicker'>GET GOING FAST</p></div>"
            "<h1>CMNET2 Colorization Studio</h1>"
            "<p class='brand-copy'>Standalone local CUDA reference-based colorization for images and videos. "
            "Load a grayscale target, provide one or more color references, and write the finished output locally.</p>"
            "<div class='brand-chips'>"
            "<span class='brand-chip'>CUDA required</span>"
            "<span class='brand-chip'>Image colorization</span>"
            "<span class='brand-chip'>Video colorization</span>"
            "<span class='brand-chip'>Local output folder</span>"
            "</div>"
            "</div>"
        )

        with gr.Row():
            with gr.Column(scale=7):
                with gr.Tab("Video"):
                    with gr.Group(elem_classes=["panel"]):
                        video_input = gr.Video(
                            label="Target video",
                            value=str(ROOT / "assets" / "video_full" / "sample_bw_full.mp4"),
                        )
                        video_refs = gr.File(
                            label="Reference frames (optional upload)",
                            file_count="multiple",
                            type="filepath",
                        )
                        ref_folder = gr.Textbox(
                            label="Reference folder path",
                            value=str(ROOT / "assets" / "video_full" / "ref"),
                        )
                        video_output_name = gr.Textbox(label="Output filename", value="cmnet2_video_output.mp4")
                        with gr.Accordion("Advanced video options", open=True):
                            with gr.Row():
                                max_side = gr.Slider(256, 2048, value=512, step=16, label="Max side")
                                window_size = gr.Slider(0, 250, value=40, step=1, label="Window size")
                            with gr.Row():
                                top_k = gr.Slider(1, 60, value=30, step=1, label="Top K")
                                mem_every = gr.Slider(1, 20, value=5, step=1, label="Memory every N frames")
                        run_video = gr.Button("Colorize Video", variant="primary", size="lg", elem_classes=["run-button"])

                with gr.Tab("Image"):
                    with gr.Group(elem_classes=["panel"]):
                        image_input = gr.Image(
                            label="Target image",
                            type="filepath",
                            value=str(ROOT / "assets" / "image" / "image_bw.jpg"),
                        )
                        image_ref = gr.Image(
                            label="Reference image",
                            type="filepath",
                            value=str(ROOT / "assets" / "image" / "image_color_ref.jpg"),
                        )
                        image_output_name = gr.Textbox(label="Output filename", value="cmnet2_image_output.jpg")
                        run_image = gr.Button("Colorize Image", variant="primary", size="lg", elem_classes=["run-button"])

            with gr.Column(scale=5):
                output_image = gr.Image(label="Image output", type="filepath", height=330)
                output_video = gr.Video(label="Video output", height=330)
                log = gr.Textbox(label="Status / log", value=status(), lines=18, elem_classes=["status-box"])
                refresh = gr.Button("Refresh status", elem_classes=["utility-button"])

        run_image.click(
            fn=colorize_image,
            inputs=[image_input, image_ref, image_output_name],
            outputs=[output_image, log],
        )
        run_video.click(
            fn=colorize_video,
            inputs=[video_input, video_refs, ref_folder, video_output_name, max_side, window_size, top_k, mem_every],
            outputs=[output_video, log],
        )
        refresh.click(fn=status, inputs=[], outputs=[log])

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="GGF CMNET2 standalone app")
    parser.add_argument("--host", default=os.environ.get("GGF_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("GGF_PORT", "7867")))
    args = parser.parse_args()

    ROOT.joinpath("outputs").mkdir(exist_ok=True)
    build_app().queue(default_concurrency_limit=1).launch(
        server_name=args.host,
        server_port=args.port,
        inbrowser=True,
        theme=gr.themes.Soft(primary_hue="red", neutral_hue="stone"),
        css=CSS,
        footer_links=[],
    )


if __name__ == "__main__":
    main()
