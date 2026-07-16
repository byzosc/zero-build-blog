from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "posts" / "2026-07-16-motionhub"
FFMPEG = shutil.which("ffmpeg")

BG = "#05070c"
PANEL = "#0d1119"
LINE = "#263044"
WHITE = "#f6f8fb"
MUTED = "#9aa6b8"
TEAL = "#42dcc6"
PINK = "#ff5da2"
BLUE = "#79a8ff"

FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")


def run(*args: str) -> None:
    subprocess.run(args, check=True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BOLD if bold else FONT_REGULAR), size=size)


def fit_image(
    canvas: Image.Image,
    source: Image.Image,
    box: tuple[int, int, int, int],
    *,
    background: str | None = None,
) -> tuple[int, int, int, int, float]:
    x, y, width, height = box
    scale = min(width / source.width, height / source.height)
    out_width = round(source.width * scale)
    out_height = round(source.height * scale)
    out_x = x + (width - out_width) // 2
    out_y = y + (height - out_height) // 2
    if background:
        ImageDraw.Draw(canvas).rounded_rectangle(
            (x, y, x + width, y + height), radius=6, fill=background, outline=LINE, width=2
        )
    resized = source.resize((out_width, out_height), Image.Resampling.LANCZOS)
    canvas.paste(resized, (out_x, out_y))
    return out_x, out_y, out_width, out_height, scale


def draw_brand(draw: ImageDraw.ImageDraw, width: int, *, y: int = 44) -> None:
    draw.text((64, y), "MOTIONHUB", font=font(28, True), fill=WHITE)
    draw.text((280, y + 3), "MOTIONSHEET + MOTIONPILOT", font=font(18), fill=TEAL)
    draw.line((64, y + 48, width - 64, y + 48), fill=LINE, width=2)


def draw_footer(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    draw.text((64, height - 54), "ZERB LION / 2026", font=font(17, True), fill=MUTED)
    draw.text((width - 350, height - 54), "github.com/zerbLion", font=font(17), fill=MUTED)


def make_title_card(size: tuple[int, int], vertical: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width, y=42 if vertical else 48)

    if vertical:
        draw.text((64, 230), "手K动效已死？", font=font(82, True), fill=WHITE)
        draw.text((64, 340), "AI 正在接管 AE", font=font(82, True), fill=WHITE)
        draw.rounded_rectangle((64, 492, 1016, 500), radius=4, fill=LINE)
        draw.rounded_rectangle((64, 492, 670, 500), radius=4, fill=PINK)
        draw.text((64, 555), "不是生成一段黑盒视频", font=font(34, True), fill=TEAL)
        draw.text((64, 612), "而是把可编辑图层和关键帧写回 After Effects", font=font(26), fill=MUTED)
        draw.text((64, 815), "MotionSheet", font=font(35, True), fill=WHITE)
        draw.text((64, 864), "读懂时间 / 曲线 / 层级", font=font(23), fill=MUTED)
        draw.text((64, 1000), "MotionPilot", font=font(35, True), fill=WHITE)
        draw.text((64, 1049), "理解意图 / 执行 / 保留可编辑结果", font=font(23), fill=MUTED)
    else:
        draw.text((104, 230), "手K动效已死？", font=font(108, True), fill=WHITE)
        draw.text((104, 368), "AI 正在接管 AE", font=font(108, True), fill=WHITE)
        draw.rounded_rectangle((106, 536, 1120, 546), radius=5, fill=LINE)
        draw.rounded_rectangle((106, 536, 748, 546), radius=5, fill=PINK)
        draw.text((106, 600), "MotionSheet 读懂动效", font=font(34, True), fill=TEAL)
        draw.text((106, 656), "MotionPilot 把意图写回可编辑的 AE 图层与关键帧", font=font(29), fill=MUTED)
        draw.text((106, 782), "MOTION SPEC  →  AI PLAN  →  EDITABLE AE", font=font(24, True), fill=BLUE)
    draw_footer(draw, width, height)
    return image


def make_bridge_card(size: tuple[int, int], vertical: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)
    if vertical:
        draw.text((64, 290), "AI 不负责替你审美", font=font(63, True), fill=WHITE)
        draw.text((64, 385), "它负责把意图执行到底", font=font(63, True), fill=WHITE)
        entries = [
            ("READ", "MotionSheet", "把动效拆成结构和规范", TEAL),
            ("PLAN", "LLM", "把自然语言压成受控计划", BLUE),
            ("WRITE", "MotionPilot", "把计划写成 AE 可编辑关键帧", PINK),
        ]
        y = 585
        for tag, name, desc, color in entries:
            draw.text((64, y), tag, font=font(21, True), fill=color)
            draw.text((190, y - 8), name, font=font(34, True), fill=WHITE)
            draw.text((190, y + 43), desc, font=font(23), fill=MUTED)
            y += 185
    else:
        draw.text((96, 260), "AI 不负责替你审美", font=font(82, True), fill=WHITE)
        draw.text((96, 365), "它负责把意图执行到底", font=font(82, True), fill=WHITE)
        draw.text((100, 560), "READ", font=font(22, True), fill=TEAL)
        draw.text((100, 600), "MotionSheet", font=font(40, True), fill=WHITE)
        draw.text((100, 660), "时间 / 曲线 / 图层 / 层级", font=font(24), fill=MUTED)
        draw.text((720, 560), "PLAN", font=font(22, True), fill=BLUE)
        draw.text((720, 600), "LLM", font=font(40, True), fill=WHITE)
        draw.text((720, 660), "自然语言 → 受控 motion plan", font=font(24), fill=MUTED)
        draw.text((1280, 560), "WRITE", font=font(22, True), fill=PINK)
        draw.text((1280, 600), "MotionPilot", font=font(40, True), fill=WHITE)
        draw.text((1280, 660), "可编辑图层 / 关键帧 / 效果", font=font(24), fill=MUTED)
        draw.line((430, 632, 660, 632), fill=LINE, width=4)
        draw.polygon(((660, 632), (638, 620), (638, 644)), fill=TEAL)
        draw.line((1000, 632, 1220, 632), fill=LINE, width=4)
        draw.polygon(((1220, 632), (1198, 620), (1198, 644)), fill=PINK)
    draw_footer(draw, width, height)
    return image


def make_media_base(
    size: tuple[int, int],
    label: str,
    headline: str,
    detail: str,
    *,
    vertical: bool = False,
) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)
    if vertical:
        draw.text((64, 145), label, font=font(26, True), fill=TEAL if label.startswith("01") else PINK)
        draw.text((64, 195), headline, font=font(54, True), fill=WHITE)
        draw.text((64, 272), detail, font=font(23), fill=MUTED)
    else:
        draw.text((72, 118), label, font=font(24, True), fill=TEAL if label.startswith("01") else PINK)
        draw.text((72, 154), headline, font=font(42, True), fill=WHITE)
        draw.text((72, 213), detail, font=font(23), fill=MUTED)
    draw_footer(draw, width, height)
    return image


def make_outro(size: tuple[int, int], vertical: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)
    if vertical:
        draw.text((64, 290), "MotionHub", font=font(98, True), fill=WHITE)
        draw.text((64, 420), "读懂动效，再把意图写回 AE", font=font(42, True), fill=TEAL)
        draw.text((64, 590), "现在：两个可工作的原型", font=font(29), fill=MUTED)
        draw.text((64, 648), "下一步：打通统一 motion contract", font=font(29), fill=MUTED)
        draw.text((64, 910), "MotionSheet", font=font(32, True), fill=WHITE)
        draw.text((64, 965), "github.com/zerbLion/keyframe_sheet", font=font(21), fill=MUTED)
        draw.text((64, 1085), "MotionPilot", font=font(32, True), fill=WHITE)
        draw.text((64, 1140), "github.com/zerbLion/motion-design", font=font(21), fill=MUTED)
    else:
        draw.text((116, 260), "MotionHub", font=font(118, True), fill=WHITE)
        draw.text((116, 420), "读懂动效，再把意图写回 AE", font=font(48, True), fill=TEAL)
        draw.text((116, 555), "MotionSheet  ×  MotionPilot", font=font(34, True), fill=MUTED)
        draw.text((116, 700), "现在：两个可工作的原型", font=font(26), fill=WHITE)
        draw.text((116, 754), "下一步：统一 motion contract，真正接通分析与执行", font=font(26), fill=MUTED)
        draw.text((116, 860), "github.com/zerbLion", font=font(22), fill=BLUE)
    draw_footer(draw, width, height)
    return image


def save_segment_still(source: Path, output: Path, duration: float) -> None:
    fade_out = max(duration - 0.12, 0)
    run(
        FFMPEG,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-loop",
        "1",
        "-i",
        str(source),
        "-t",
        str(duration),
        "-vf",
        f"fps=30,fade=t=in:st=0:d=0.12,fade=t=out:st={fade_out}:d=0.12,format=yuv420p",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        str(output),
    )


def save_segment_overlay(
    background: Path,
    motion: Path,
    output: Path,
    duration: float,
    rect: tuple[int, int, int, int],
    *,
    gif: bool = False,
) -> None:
    x, y, width, height = rect
    fade_out = max(duration - 0.12, 0)
    motion_options = ["-stream_loop", "-1"] if not gif else ["-ignore_loop", "0"]
    run(
        FFMPEG,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-loop",
        "1",
        "-i",
        str(background),
        *motion_options,
        "-i",
        str(motion),
        "-t",
        str(duration),
        "-filter_complex",
        (
            f"[1:v]fps=30,scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black[m];"
            f"[0:v][m]overlay={x}:{y}:shortest=1,"
            f"fade=t=in:st=0:d=0.12,fade=t=out:st={fade_out}:d=0.12,format=yuv420p[v]"
        ),
        "-map",
        "[v]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        str(output),
    )


def build_video(vertical: bool, work: Path) -> None:
    size = (1080, 1440) if vertical else (1920, 1080)
    suffix = "v" if vertical else "h"
    title = work / f"title-{suffix}.png"
    motion_base = work / f"motion-{suffix}.png"
    bridge = work / f"bridge-{suffix}.png"
    ae_base = work / f"ae-{suffix}.png"
    final_base = work / f"final-{suffix}.png"
    outro = work / f"outro-{suffix}.png"

    make_title_card(size, vertical).save(title)
    make_bridge_card(size, vertical).save(bridge)
    make_outro(size, vertical).save(outro)

    motion_image = make_media_base(
        size,
        "01 / MOTIONSHEET",
        "先让动效变得可读",
        "Lottie → 图层、时间、曲线、层级与交接表",
        vertical=vertical,
    )
    ae_image = make_media_base(
        size,
        "02 / MOTIONPILOT",
        "再把意图写回 After Effects",
        "真实 60fps AE 渲染，不是两张截图做推拉",
        vertical=vertical,
    )
    final_image = make_media_base(
        size,
        "EDITABLE RESULT",
        "结果仍然留在 AE 工作流里",
        "图层、关键帧、效果继续可调，不交付黑盒视频",
        vertical=vertical,
    )

    gif_preview = Image.open(POST / "motionsheet-demo.gif").convert("RGB")
    ae_ui = Image.open(POST / "ae-motionpilot.png").convert("RGB")
    crop_box = (360, 45, 1278, 550)
    ae_crop = ae_ui.crop(crop_box)

    if vertical:
        motion_rect = (40, 360, 1000, 476)
        draw = ImageDraw.Draw(motion_image)
        draw.rounded_rectangle((38, 358, 1042, 838), radius=6, fill=PANEL, outline=LINE, width=2)

        ae_x, ae_y, ae_w, ae_h, ae_scale = fit_image(ae_image, ae_crop, (40, 340, 1000, 760), background=PANEL)
        viewport_x = round(ae_x + (368 - crop_box[0]) * ae_scale)
        viewport_y = round(ae_y + (113 - crop_box[1]) * ae_scale)
        viewport_w = round(614 * ae_scale)
        viewport_h = round(418 * ae_scale)
        video_h = round(viewport_w * 9 / 16)
        ae_rect = (viewport_x, viewport_y + (viewport_h - video_h) // 2, viewport_w, video_h)

        final_rect = (0, 390, 1080, 608)
    else:
        motion_rect = (90, 270, 1740, 720)
        draw = ImageDraw.Draw(motion_image)
        draw.rounded_rectangle((88, 268, 1832, 994), radius=6, fill=PANEL, outline=LINE, width=2)

        ae_x, ae_y, ae_w, ae_h, ae_scale = fit_image(ae_image, ae_crop, (90, 255, 1740, 755), background=PANEL)
        viewport_x = round(ae_x + (368 - crop_box[0]) * ae_scale)
        viewport_y = round(ae_y + (113 - crop_box[1]) * ae_scale)
        viewport_w = round(614 * ae_scale)
        viewport_h = round(418 * ae_scale)
        video_h = round(viewport_w * 9 / 16)
        ae_rect = (viewport_x, viewport_y + (viewport_h - video_h) // 2, viewport_w, video_h)

        final_rect = (260, 220, 1400, 788)

    motion_image.save(motion_base)
    ae_image.save(ae_base)
    final_image.save(final_base)

    segments = [work / f"{suffix}-{index:02}.mp4" for index in range(1, 7)]
    save_segment_still(title, segments[0], 2.6)
    save_segment_overlay(
        motion_base,
        POST / "motionsheet-demo.gif",
        segments[1],
        6.4,
        motion_rect,
        gif=True,
    )
    save_segment_still(bridge, segments[2], 2.4)
    save_segment_overlay(
        ae_base,
        POST / "ae-motion-result.mp4",
        segments[3],
        4.0,
        ae_rect,
    )
    save_segment_overlay(
        final_base,
        POST / "ae-motion-result.mp4",
        segments[4],
        4.0,
        final_rect,
    )
    save_segment_still(outro, segments[5], 3.0)

    joined = work / f"joined-{suffix}.mp4"
    concat_inputs: list[str] = []
    for segment in segments:
        concat_inputs.extend(("-i", str(segment)))
    concat_filter = "".join(
        f"[{index}:v]setpts=PTS-STARTPTS[v{index}];" for index in range(len(segments))
    ) + "".join(f"[v{index}]" for index in range(len(segments))) + (
        f"concat=n={len(segments)}:v=1:a=0,fps=30,format=yuv420p[v]"
    )
    run(
        FFMPEG,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        *concat_inputs,
        "-filter_complex",
        concat_filter,
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        str(joined),
    )

    output = POST / ("motionhub-demo-vertical.mp4" if vertical else "motionhub-demo.mp4")
    run(
        FFMPEG,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(joined),
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output),
    )


def make_cover(ae_still: Image.Image, vertical: bool = False) -> Image.Image:
    size = (1080, 1440) if vertical else (1600, 900)
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)

    if vertical:
        draw.text((64, 180), "手K动效已死？", font=font(78, True), fill=WHITE)
        draw.text((64, 282), "AI 正在接管 AE", font=font(78, True), fill=WHITE)
        draw.text((64, 410), "MotionSheet × MotionPilot = MotionHub", font=font(26, True), fill=TEAL)
        fit_image(image, ae_still, (30, 500, 1020, 574), background=PANEL)
        draw.text((64, 1140), "读懂动效", font=font(31, True), fill=WHITE)
        draw.text((64, 1190), "→ 生成受控计划", font=font(31, True), fill=BLUE)
        draw.text((64, 1240), "→ 写回 AE 可编辑关键帧", font=font(31, True), fill=PINK)
    else:
        draw.text((82, 175), "手K动效已死？", font=font(84, True), fill=WHITE)
        draw.text((82, 285), "AI 正在接管 AE", font=font(84, True), fill=WHITE)
        draw.text((84, 420), "MotionSheet × MotionPilot = MotionHub", font=font(27, True), fill=TEAL)
        draw.text((84, 520), "读懂动效", font=font(31, True), fill=WHITE)
        draw.text((84, 573), "生成受控计划", font=font(31, True), fill=BLUE)
        draw.text((84, 626), "写回 AE 可编辑关键帧", font=font(31, True), fill=PINK)
        fit_image(image, ae_still, (800, 135, 740, 620), background=PANEL)
    draw_footer(draw, width, height)
    return image


def main() -> None:
    if not FFMPEG:
        raise RuntimeError("ffmpeg is required")
    if not (POST / "ae-motion-result.mp4").exists():
        raise FileNotFoundError("Missing ae-motion-result.mp4")

    with tempfile.TemporaryDirectory(prefix="motionhub-launch-") as temp:
        work = Path(temp)
        ae_still_path = work / "ae-still.png"
        run(
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            "0.35",
            "-i",
            str(POST / "ae-motion-result.mp4"),
            "-frames:v",
            "1",
            str(ae_still_path),
        )
        ae_still = Image.open(ae_still_path).convert("RGB")
        make_cover(ae_still).save(POST / "cover.png", optimize=True)
        make_cover(ae_still, vertical=True).save(POST / "social-cover.png", optimize=True)
        build_video(False, work)
        build_video(True, work)


if __name__ == "__main__":
    main()
