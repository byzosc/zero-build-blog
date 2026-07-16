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


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    position: tuple[int, int],
    max_width: int,
    text_font: ImageFont.FreeTypeFont,
    fill: str,
    *,
    line_gap: int = 8,
) -> int:
    x, y = position
    lines: list[str] = []
    current = ""
    for character in text:
        candidate = current + character
        if current and draw.textlength(candidate, font=text_font) > max_width:
            lines.append(current)
            current = character
        else:
            current = candidate
    if current:
        lines.append(current)
    line_height = text_font.size + line_gap
    for index, line in enumerate(lines):
        draw.text((x, y + index * line_height), line, font=text_font, fill=fill)
    return y + len(lines) * line_height


def split_geometry(vertical: bool) -> dict[str, tuple[int, ...]]:
    if vertical:
        return {
            "left": (40, 280, 620, 900),
            "right": (680, 280, 360, 900),
            "comp": (60, 380, 580, 326),
            "prompt": (700, 470, 320, 225),
            "button": (700, 802, 320, 62),
            "status": (700, 890, 320, 230),
            "timeline": (70, 1100, 630),
        }
    return {
        "left": (64, 190, 1220, 780),
        "right": (1320, 190, 536, 780),
        "comp": (88, 260, 1168, 657),
        "prompt": (1350, 382, 476, 210),
        "button": (1350, 700, 476, 64),
        "status": (1350, 790, 476, 140),
        "timeline": (100, 943, 1248),
    }


def make_split_base(size: tuple[int, int], vertical: bool) -> tuple[Image.Image, dict[str, tuple[int, ...]]]:
    width, height = size
    geometry = split_geometry(vertical)
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width, y=36 if vertical else 34)

    if vertical:
        draw.text((40, 124), "一句话，AE 自动做出来", font=font(48, True), fill=WHITE)
        draw.text((40, 190), "右边描述，左边生成；结果仍然可以继续编辑", font=font(23), fill=TEAL)
    else:
        draw.text((64, 102), "一句话，AE 自动做出来", font=font(50, True), fill=WHITE)
        draw.text((770, 118), "右边描述  →  左边生成  →  关键帧继续可调", font=font(25, True), fill=TEAL)

    left_x, left_y, left_w, left_h = geometry["left"]
    draw.rounded_rectangle(
        (left_x, left_y, left_x + left_w, left_y + left_h),
        radius=6,
        fill="#111318",
        outline=LINE,
        width=2,
    )
    draw.rectangle((left_x + 1, left_y + 1, left_x + left_w - 1, left_y + 55), fill="#1b1d22")
    draw.text((left_x + 22, left_y + 16), "Composition  /  Active Camera", font=font(19, True), fill=WHITE)
    draw.ellipse((left_x + left_w - 48, left_y + 18, left_x + left_w - 28, left_y + 38), fill="#2f7df6")

    comp_x, comp_y, comp_w, comp_h = geometry["comp"]
    draw.rectangle((comp_x, comp_y, comp_x + comp_w, comp_y + comp_h), fill="#010205", outline="#303746", width=2)

    if vertical:
        draw.text((60, 742), "EDITABLE RESULT", font=font(18, True), fill=PINK)
        draw.text((60, 775), "8 independent Shape Layers", font=font(24, True), fill=WHITE)
        for index in range(8):
            track_y = 828 + index * 31
            draw.text((62, track_y - 2), f"Petal {index + 1:02}", font=font(14), fill=MUTED)
            draw.rounded_rectangle((172, track_y, 622, track_y + 12), radius=4, fill="#202631")
            key_x = 220 + index * 31
            draw.polygon(((key_x, track_y + 6), (key_x + 6, track_y), (key_x + 12, track_y + 6), (key_x + 6, track_y + 12)), fill=BLUE)
            end_x = 500 + (index % 3) * 24
            draw.polygon(((end_x, track_y + 6), (end_x + 6, track_y), (end_x + 12, track_y + 6), (end_x + 6, track_y + 12)), fill=PINK)
    else:
        draw.text((left_x + 24, 927), "8 editable Shape Layers", font=font(17, True), fill=WHITE)
        for index in range(8):
            track_x = 310 + index * 104
            draw.rounded_rectangle((track_x, 942, track_x + 78, 955), radius=4, fill="#202631")
            draw.polygon(((track_x + 10, 948), (track_x + 16, 942), (track_x + 22, 948), (track_x + 16, 954)), fill=BLUE)
            draw.polygon(((track_x + 56, 948), (track_x + 62, 942), (track_x + 68, 948), (track_x + 62, 954)), fill=PINK)

    right_x, right_y, right_w, right_h = geometry["right"]
    draw.rounded_rectangle(
        (right_x, right_y, right_x + right_w, right_y + right_h),
        radius=6,
        fill="#171719",
        outline=LINE,
        width=2,
    )
    header_font = font(21 if vertical else 25, True)
    small_font = font(15 if vertical else 18)
    draw.text((right_x + 22, right_y + 20), "MotionPilot", font=header_font, fill="#65c4ff")
    draw.text((right_x + right_w - (126 if vertical else 164), right_y + 23), "Bridge ON", font=small_font, fill="#74e27b")
    draw.line((right_x + 20, right_y + 62, right_x + right_w - 20, right_y + 62), fill="#35383e", width=2)
    draw.text((right_x + 38, right_y + 84), "Generate", font=small_font, fill="#65c4ff")
    draw.text((right_x + right_w - 115, right_y + 84), "Settings", font=small_font, fill=MUTED)
    draw.line((right_x + 18, right_y + 116, right_x + right_w - 18, right_y + 116), fill="#2e70dc", width=3)
    draw.text((right_x + 22, right_y + 139), "Preset", font=small_font, fill=MUTED)
    draw.rounded_rectangle(
        (right_x + 22, right_y + 167, right_x + right_w - 22, right_y + 213),
        radius=5,
        fill="#202023",
        outline="#45464b",
        width=1,
    )
    draw.text((right_x + 36, right_y + 180), "Free — describe anything", font=small_font, fill=WHITE)

    prompt_x, prompt_y, prompt_w, prompt_h = geometry["prompt"]
    draw.text((prompt_x, prompt_y - 30), "Describe motion", font=small_font, fill=MUTED)
    draw.rounded_rectangle(
        (prompt_x, prompt_y, prompt_x + prompt_w, prompt_y + prompt_h),
        radius=5,
        fill="#202023",
        outline="#4a4b50",
        width=2,
    )

    model_y = prompt_y + prompt_h + 22
    draw.rounded_rectangle(
        (prompt_x, model_y, prompt_x + prompt_w, model_y + 54),
        radius=5,
        fill="#202023",
        outline="#45464b",
        width=1,
    )
    draw.text((prompt_x + 16, model_y + 15), "AI planner  /  Vision on", font=small_font, fill=WHITE)

    status_x, status_y, status_w, status_h = geometry["status"]
    draw.rounded_rectangle(
        (status_x, status_y, status_x + status_w, status_y + status_h),
        radius=5,
        fill="#101216",
        outline="#353943",
        width=1,
    )
    draw.text((status_x + 16, status_y + 14), "EXECUTION", font=font(14 if vertical else 16, True), fill=MUTED)

    footer_text = "左侧：真实 Comp 4 渲染  |  右侧：MotionPilot 面板演示拼接"
    draw.text((40 if vertical else 64, height - 48), footer_text, font=font(15 if vertical else 17), fill=MUTED)
    return image, geometry


def draw_split_frame(
    base: Image.Image,
    geometry: dict[str, tuple[int, ...]],
    time_seconds: float,
    motion_frame: Image.Image | None,
    *,
    vertical: bool,
    duration: float = 11.6,
) -> Image.Image:
    frame = base.copy()
    draw = ImageDraw.Draw(frame)
    prompt = "8 瓣发光花环向中心旋转收拢成圆，再反向展开；节奏放慢 2×"
    visible_count = min(len(prompt), round(max(0.0, time_seconds) / 2.45 * len(prompt)))
    prompt_x, prompt_y, prompt_w, prompt_h = geometry["prompt"]
    prompt_font = font(18 if vertical else 23)
    draw_wrapped_text(
        draw,
        prompt[:visible_count],
        (prompt_x + 16, prompt_y + 18),
        prompt_w - 32,
        prompt_font,
        WHITE,
        line_gap=9,
    )

    button_x, button_y, button_w, button_h = geometry["button"]
    clicked = time_seconds >= 2.7
    button_fill = "#2f6fe7" if not clicked else "#2459b9"
    draw.rounded_rectangle(
        (button_x, button_y, button_x + button_w, button_y + button_h),
        radius=5,
        fill=button_fill,
    )
    button_text = "Generate" if not clicked else "Generating…"
    button_font = font(19 if vertical else 23, True)
    button_box = draw.textbbox((0, 0), button_text, font=button_font)
    draw.text(
        (
            button_x + (button_w - (button_box[2] - button_box[0])) // 2,
            button_y + (button_h - (button_box[3] - button_box[1])) // 2 - 2,
        ),
        button_text,
        font=button_font,
        fill=WHITE,
    )
    if 2.7 <= time_seconds <= 3.15:
        progress = (time_seconds - 2.7) / 0.45
        radius = 16 + round(progress * 42)
        center_x = button_x + button_w // 2
        center_y = button_y + button_h // 2
        ring = "#80b3ff" if progress < 0.55 else "#456ca8"
        draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), outline=ring, width=4)

    if time_seconds < 2.7:
        status = "等待描述…"
        status_color = MUTED
    elif time_seconds < 3.1:
        status = "读取当前合成：8 个图层"
        status_color = BLUE
    elif time_seconds < 3.4:
        status = "规划空间旋转、收拢与节奏"
        status_color = TEAL
    elif time_seconds < 11.15:
        status = "正在写入可编辑关键帧…"
        status_color = PINK
    else:
        status = "完成：8 个 Shape Layers"
        status_color = "#74e27b"

    status_x, status_y, status_w, status_h = geometry["status"]
    draw.ellipse((status_x + 16, status_y + 51, status_x + 30, status_y + 65), fill=status_color)
    status_font = font(17 if vertical else 21, True)
    draw_wrapped_text(
        draw,
        status,
        (status_x + 42, status_y + 46),
        status_w - 58,
        status_font,
        WHITE,
        line_gap=8,
    )
    if time_seconds >= 3.4:
        detail_font = font(14 if vertical else 17)
        draw.text((status_x + 18, status_y + 102), "runBatch  /  editable keys  /  no video bake", font=detail_font, fill=MUTED)

    comp_x, comp_y, comp_w, comp_h = geometry["comp"]
    if motion_frame is None or time_seconds < 3.4:
        waiting_font = font(23 if vertical else 30, True)
        waiting = "等待右侧生成…"
        waiting_box = draw.textbbox((0, 0), waiting, font=waiting_font)
        draw.text(
            (
                comp_x + (comp_w - (waiting_box[2] - waiting_box[0])) // 2,
                comp_y + (comp_h - (waiting_box[3] - waiting_box[1])) // 2,
            ),
            waiting,
            font=waiting_font,
            fill="#526070",
        )
    else:
        resized = motion_frame.resize((comp_w, comp_h), Image.Resampling.LANCZOS)
        fade = min(1.0, max(0.0, (time_seconds - 3.4) / 0.18))
        if fade < 1.0:
            resized = Image.blend(Image.new("RGB", (comp_w, comp_h), "#010205"), resized, fade)
        frame.paste(resized, (comp_x, comp_y))

    timeline_start, timeline_y, timeline_end = geometry["timeline"]
    motion_progress = min(1.0, max(0.0, (time_seconds - 3.4) / 8.0))
    playhead_x = round(timeline_start + (timeline_end - timeline_start) * motion_progress)
    draw.line((playhead_x, timeline_y - 12, playhead_x, timeline_y + 20), fill="#4ba0ff", width=3)
    draw.polygon(((playhead_x - 7, timeline_y - 14), (playhead_x + 7, timeline_y - 14), (playhead_x, timeline_y - 5)), fill="#4ba0ff")

    edge_fade = 1.0
    if time_seconds < 0.12:
        edge_fade = time_seconds / 0.12
    elif time_seconds > duration - 0.12:
        edge_fade = (duration - time_seconds) / 0.12
    if edge_fade < 1.0:
        frame = Image.blend(Image.new("RGB", frame.size, BG), frame, max(0.0, edge_fade))
    return frame


def make_motion_loop(source: Path, output: Path) -> None:
    if output.exists():
        return
    run(
        FFMPEG,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-filter_complex",
        "[0:v]fps=30,split=2[forward][reverse];[reverse]reverse[back];[forward][back]concat=n=2:v=1:a=0,fps=30,format=yuv420p[v]",
        "-map",
        "[v]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        str(output),
    )


def build_split_segment(
    size: tuple[int, int],
    motion_loop: Path,
    output: Path,
    *,
    vertical: bool,
    duration: float = 11.6,
) -> None:
    width, height = size
    base, geometry = make_split_base(size, vertical)
    frame_bytes = 1920 * 1080 * 3
    decoder = subprocess.Popen(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(motion_loop),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ],
        stdout=subprocess.PIPE,
    )
    encoder = subprocess.Popen(
        [
            FFMPEG,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-s",
            f"{width}x{height}",
            "-r",
            "30",
            "-i",
            "-",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
        stdin=subprocess.PIPE,
    )
    if decoder.stdout is None or encoder.stdin is None:
        raise RuntimeError("Unable to open ffmpeg frame pipes")

    current_motion: Image.Image | None = None
    decoded_index = -1
    total_frames = round(duration * 30)
    try:
        for output_index in range(total_frames):
            time_seconds = output_index / 30
            desired_index = -1 if time_seconds < 3.4 else min(239, int((time_seconds - 3.4) * 30))
            while decoded_index < desired_index:
                data = decoder.stdout.read(frame_bytes)
                if len(data) != frame_bytes:
                    break
                current_motion = Image.frombytes("RGB", (1920, 1080), data)
                decoded_index += 1
            composed = draw_split_frame(
                base,
                geometry,
                time_seconds,
                current_motion,
                vertical=vertical,
                duration=duration,
            )
            encoder.stdin.write(composed.tobytes())
    finally:
        encoder.stdin.close()
        decoder.stdout.close()
    encoder_code = encoder.wait()
    decoder.wait()
    if encoder_code != 0:
        raise RuntimeError(f"ffmpeg split-segment encoder failed with {encoder_code}")


def make_open_source_card(size: tuple[int, int], vertical: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)
    if vertical:
        draw.text((64, 150), "插件不是捷径", font=font(58, True), fill=WHITE)
        draw.text((64, 228), "它是 AI 操作 AE 的公共底座", font=font(48, True), fill=TEAL)
        columns = [
            (70, 350, 940, 320, "没有插件", "每个效果重新写 JSX\n反复踩 AE API / 编码 / 桥接坑\n错误率高，成果难复用", PINK),
            (70, 710, 940, 320, "有 MotionPilot", "读场景、白名单执行、关键帧与回传只做一次\n以后只扩展新的 motion primitive", TEAL),
        ]
        for x, y, panel_w, panel_h, title, body, color in columns:
            draw.rounded_rectangle((x, y, x + panel_w, y + panel_h), radius=6, fill=PANEL, outline=LINE, width=2)
            draw.text((x + 28, y + 28), title, font=font(32, True), fill=color)
            draw.multiline_text((x + 28, y + 88), body, font=font(24), fill=WHITE, spacing=18)
        draw.text((64, 1115), "准备转为 MIT 开源", font=font(39, True), fill=BLUE)
        draw.text((64, 1175), "一个人补一种能力，所有人和所有 AI 都能复用", font=font(26), fill=MUTED)
    else:
        draw.text((88, 150), "插件不是捷径，是 AI 操作 AE 的公共底座", font=font(66, True), fill=WHITE)
        panels = [
            (88, 300, 820, 500, "没有插件", ["每个参考都重新写 JSX", "反复踩 AE API / 编码 / 桥接坑", "错误率高，成果难复用"], PINK),
            (1012, 300, 820, 500, "有 MotionPilot", ["读场景、执行、关键帧与回传只做一次", "以后只扩展新的 motion primitive", "每次贡献都会永久增加能力"], TEAL),
        ]
        for x, y, panel_w, panel_h, title, rows, color in panels:
            draw.rounded_rectangle((x, y, x + panel_w, y + panel_h), radius=6, fill=PANEL, outline=LINE, width=2)
            draw.text((x + 34, y + 38), title, font=font(42, True), fill=color)
            for index, row in enumerate(rows):
                row_y = y + 145 + index * 96
                draw.ellipse((x + 36, row_y + 10, x + 52, row_y + 26), fill=color)
                draw.text((x + 72, row_y), row, font=font(27), fill=WHITE)
        draw.text((90, 855), "准备转为 MIT 开源：一个人补一种能力，所有人和所有 AI 都能复用", font=font(30, True), fill=BLUE)
    draw_footer(draw, width, height)
    return image


def make_vision_card(size: tuple[int, int], vertical: bool = False) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    draw_brand(draw, width)
    if vertical:
        draw.text((64, 175), "真正的产品不是一朵花", font=font(58, True), fill=WHITE)
        draw.text((64, 260), "而是让 AI 不断学会操作 AE", font=font(52, True), fill=TEAL)
        steps = [
            ("01", "发来参考图 / GIF / 视频", BLUE),
            ("02", "AI 拆解结构与节奏", TEAL),
            ("03", "MotionPilot 写入可编辑 AE", PINK),
            ("04", "人继续调审美与细节", WHITE),
        ]
        y = 430
        for number, label, color in steps:
            draw.text((64, y), number, font=font(24, True), fill=color)
            draw.text((150, y - 8), label, font=font(34, True), fill=WHITE)
            if y < 970:
                draw.line((95, y + 52, 95, y + 105), fill=LINE, width=4)
            y += 175
        draw.text((64, 1160), "今天还做不到“任何动效”", font=font(27, True), fill=MUTED)
        draw.text((64, 1210), "但每个开源贡献都会把边界向外推一次", font=font(27, True), fill=BLUE)
    else:
        draw.text((96, 165), "真正的产品不是一朵花", font=font(78, True), fill=WHITE)
        draw.text((96, 275), "而是让 AI 不断学会操作 AE", font=font(70, True), fill=TEAL)
        steps = [
            (100, "参考图 / GIF / 视频", BLUE),
            (560, "AI 拆解", TEAL),
            (910, "MotionPilot 执行", PINK),
            (1430, "人继续打磨", WHITE),
        ]
        y = 520
        for index, (x, label, color) in enumerate(steps):
            draw.rounded_rectangle((x, y, x + 330, y + 130), radius=6, fill=PANEL, outline=color, width=3)
            draw.text((x + 28, y + 43), label, font=font(28, True), fill=WHITE)
            if index < len(steps) - 1:
                next_x = steps[index + 1][0]
                draw.line((x + 330, y + 65, next_x - 28, y + 65), fill=LINE, width=4)
                draw.polygon(((next_x - 28, y + 65), (next_x - 48, y + 53), (next_x - 48, y + 77)), fill=color)
        draw.text((100, 755), "今天还做不到“任何动效”——但每新增一个原语、效果命令和回传规则，边界就向外推一次。", font=font(27), fill=MUTED)
        draw.text((100, 835), "MotionHub  =  开源执行底座  +  AI 规划  +  人类审美", font=font(34, True), fill=BLUE)
    draw_footer(draw, width, height)
    return image


def build_video(vertical: bool, work: Path) -> None:
    size = (1080, 1440) if vertical else (1920, 1080)
    suffix = "v" if vertical else "h"
    motion_base = work / f"motion-{suffix}.png"
    open_source = work / f"open-source-{suffix}.png"
    vision = work / f"vision-{suffix}.png"
    motion_loop = work / "ae-motion-loop.mp4"

    make_motion_loop(POST / "ae-motion-result.mp4", motion_loop)
    make_open_source_card(size, vertical).save(open_source)
    make_vision_card(size, vertical).save(vision)

    motion_image = make_media_base(
        size,
        "MOTIONSHEET / READ MOTION",
        "让参考动效变成 AI 能读的结构",
        "时间 / 曲线 / 图层 / 层级 → motion contract",
        vertical=vertical,
    )

    if vertical:
        motion_rect = (40, 360, 1000, 476)
        draw = ImageDraw.Draw(motion_image)
        draw.rounded_rectangle((38, 358, 1042, 838), radius=6, fill=PANEL, outline=LINE, width=2)
    else:
        motion_rect = (90, 270, 1740, 720)
        draw = ImageDraw.Draw(motion_image)
        draw.rounded_rectangle((88, 268, 1832, 994), radius=6, fill=PANEL, outline=LINE, width=2)

    motion_image.save(motion_base)

    segments = [work / f"{suffix}-{index:02}.mp4" for index in range(1, 5)]
    build_split_segment(size, motion_loop, segments[0], vertical=vertical)
    save_segment_overlay(
        motion_base,
        POST / "motionsheet-demo.gif",
        segments[1],
        4.8,
        motion_rect,
        gif=True,
    )
    save_segment_still(open_source, segments[2], 4.2)
    save_segment_still(vision, segments[3], 4.0)

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
    size = (1080, 1440) if vertical else (1920, 1080)
    base, geometry = make_split_base(size, vertical)
    cover = draw_split_frame(base, geometry, 11.5, ae_still, vertical=vertical)
    if vertical:
        return cover
    return cover.resize((1600, 900), Image.Resampling.LANCZOS)


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
