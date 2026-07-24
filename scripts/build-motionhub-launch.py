from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "posts" / "2026-07-16-motionhub"
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")

BG = (5, 7, 12)
PANEL = (13, 17, 25)
WHITE = (246, 248, 251)
MUTED = (158, 169, 187)
TEAL = (66, 220, 198)
PINK = (255, 93, 162)
BLUE = (121, 168, 255)
LINE = (38, 48, 68)

FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")


def run(*args: object) -> None:
    subprocess.run([str(arg) for arg in args], check=True)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def duration(path: Path) -> float:
    result = subprocess.run(
        [
            str(FFPROBE),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def rounded_panel(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    *,
    fill: tuple[int, int, int, int] = (5, 7, 12, 218),
    outline: tuple[int, int, int, int] = (66, 220, 198, 170),
) -> None:
    draw.rounded_rectangle(box, radius=12, fill=fill, outline=outline, width=2)


def make_horizontal_overlays(work: Path) -> list[Path]:
    size = (1920, 1080)
    specs = [
        (
            "ae-input.png",
            "01",
            "右侧写一句话，左侧从空画布开始",
            "真实 AE 屏幕录制 / MotionPilot 面板",
            BLUE,
        ),
        (
            "ae-planning.png",
            "02",
            "AI 正在读取图层并规划",
            "原始等待已明确压缩 6x；只跳过等待，不伪造结果",
            PINK,
        ),
        (
            "ae-writeback.png",
            "03",
            "关键帧正在写回 After Effects",
            "不是生成视频：图层、属性和曲线都能继续编辑",
            TEAL,
        ),
    ]
    outputs: list[Path] = []
    for name, step, title, detail, color in specs:
        image = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        box = (34, 30, 1090, 151)
        rounded_panel(draw, box, outline=(*color, 190))
        draw.rounded_rectangle((58, 53, 132, 125), radius=8, fill=(*color, 235))
        draw.text((77, 64), step, font=font(28, True), fill=BG)
        draw.text((162, 45), title, font=font(34, True), fill=WHITE)
        draw.text((164, 99), detail, font=font(21), fill=color)
        output = work / name
        image.save(output)
        outputs.append(output)
    return outputs


def make_soft_focus_overlay(
    work: Path,
    name: str,
    center: tuple[int, int],
    radius: tuple[int, int],
    color: tuple[int, int, int],
) -> Path:
    cx, cy = center
    rx, ry = radius
    box = (cx - rx, cy - ry, cx + rx, cy + ry)

    halo = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    halo_draw = ImageDraw.Draw(halo)
    halo_draw.ellipse(box, fill=(*color, 24))
    halo = halo.filter(ImageFilter.GaussianBlur(72))

    core = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    core_draw = ImageDraw.Draw(core)
    core_draw.ellipse(box, fill=(*color, 12))
    core = core.filter(ImageFilter.GaussianBlur(28))
    halo.alpha_composite(core)

    output = work / name
    halo.save(output)
    return output


def make_ae_focus_overlays(work: Path) -> list[Path]:
    specs = [
        ("focus-input.png", (1460, 490), (390, 175), BLUE),
        ("focus-generate.png", (1500, 740), (310, 130), PINK),
        ("focus-keyframes.png", (1000, 900), (330, 130), TEAL),
        ("focus-result.png", (960, 535), (470, 315), PINK),
    ]
    return [
        make_soft_focus_overlay(work, name, center, radius, color)
        for name, center, radius, color in specs
    ]


def make_widget_overlays(work: Path) -> list[Path]:
    specs = [
        (
            "widget-input.png",
            "04",
            "再写一句，组件参数继续生成",
            "真实 AE 录屏 / 输入：手柄控制数字",
            BLUE,
        ),
        (
            "widget-planning.png",
            "05",
            "AI 读取组件并规划关键帧",
            "约 10 秒等待压缩 5x；执行与预览保持原速",
            PINK,
        ),
        (
            "widget-result.png",
            "06",
            "数字控制已经写回 AE 图层",
            "Slider 与关键帧仍可编辑，结果不是渲染视频",
            TEAL,
        ),
    ]
    outputs: list[Path] = []
    for name, step, title, detail, color in specs:
        image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        box = (34, 30, 1090, 151)
        rounded_panel(draw, box, outline=(*color, 190))
        draw.rounded_rectangle((58, 53, 132, 125), radius=8, fill=(*color, 235))
        draw.text((77, 64), step, font=font(28, True), fill=BG)
        draw.text((162, 45), title, font=font(34, True), fill=WHITE)
        draw.text((164, 99), detail, font=font(21), fill=color)
        output = work / name
        image.save(output)
        outputs.append(output)
    return outputs


def make_widget_focus_overlays(work: Path) -> list[Path]:
    specs = [
        ("widget-focus-input.png", (1510, 600), (330, 170), BLUE),
        ("widget-focus-planning.png", (1510, 340), (350, 185), PINK),
        ("widget-focus-result.png", (760, 300), (330, 235), TEAL),
        ("widget-focus-handle.png", (300, 155), (250, 105), BLUE),
    ]
    return [
        make_soft_focus_overlay(work, name, center, radius, color)
        for name, center, radius, color in specs
    ]


def make_sheet_overlays(work: Path) -> list[Path]:
    specs = [
        ("sheet-load.png", "07", "JSON 拖进浏览器", "MotionSheet 本地解析，不上传源文件", BLUE),
        ("sheet-read.png", "08", "图层、时间和曲线自动展开", "动作分组、父子关系与属性变化不再靠猜", PINK),
        ("sheet-locate.png", "09", "点一行，直接定位画面", "预览、时间轴、详情与导出保持同一个上下文", TEAL),
    ]
    outputs: list[Path] = []
    for name, step, title, detail, color in specs:
        image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 1920, 102), fill=(5, 7, 12, 236))
        draw.rounded_rectangle((42, 19, 112, 83), radius=8, fill=(*color, 235))
        draw.text((58, 29), step, font=font(26, True), fill=BG)
        draw.text((142, 18), title, font=font(35, True), fill=WHITE)
        draw.text((790, 29), detail, font=font(22), fill=color)
        output = work / name
        image.save(output)
        outputs.append(output)
    return outputs


def make_extra_sheet_overlays(work: Path) -> list[Path]:
    specs = [
        ("sheet-extra-preview.png", "10", "再换一个 JSON，结构照样能读", "真实预览与时间轴同步，不是为单个案例写死", BLUE),
        ("sheet-extra-detail.png", "11", "选中图层，动作与参数一起定位", "doc-front / doc-back / bg 的变化分别可追踪", PINK),
        ("sheet-extra-table.png", "12", "Timeline 与 Table 随时切换", "从视觉检查切到开发交付，不丢上下文", TEAL),
    ]
    outputs: list[Path] = []
    for name, step, title, detail, color in specs:
        image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 1920, 102), fill=(5, 7, 12, 236))
        draw.rounded_rectangle((42, 19, 112, 83), radius=8, fill=(*color, 235))
        draw.text((58, 29), step, font=font(26, True), fill=BG)
        draw.text((142, 18), title, font=font(35, True), fill=WHITE)
        draw.text((910, 29), detail, font=font(22), fill=color)
        output = work / name
        image.save(output)
        outputs.append(output)
    return outputs


def make_summary_overlay(work: Path) -> Path:
    image = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1920, 105), fill=(5, 7, 12, 238))
    draw.text((48, 20), "MotionPilot 写回 AE", font=font(34, True), fill=PINK)
    draw.text((442, 20), "+", font=font(34, True), fill=WHITE)
    draw.text((495, 20), "MotionSheet 读成交付", font=font(34, True), fill=TEAL)
    draw.text((1004, 25), "= MotionHub", font=font(31, True), fill=WHITE)
    draw.text((1442, 30), "开放执行底座，持续扩展能力", font=font(20), fill=MUTED)
    output = work / "summary-overlay.png"
    image.save(output)
    return output


def make_card(
    size: tuple[int, int],
    title: str,
    subtitle: str,
    output: Path,
    *,
    final: bool = False,
) -> None:
    width, height = size
    image = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(image)
    margin = 64 if width <= 1080 else 90
    draw.text((margin, 52), "MOTIONHUB", font=font(26, True), fill=WHITE)
    draw.text((margin + 205, 56), "MOTIONPILOT + MOTIONSHEET", font=font(18), fill=TEAL)
    draw.line((margin, 100, width - margin, 100), fill=LINE, width=2)

    if width <= 1080:
        title_size = 65 if not final else 58
        title_y = 470 if not final else 390
        subtitle_y = title_y + 205
        max_width = width - margin * 2
        lines = title.split("\n")
        for index, line in enumerate(lines):
            draw.text((margin, title_y + index * 88), line, font=font(title_size, True), fill=WHITE)
        draw.rounded_rectangle((margin, subtitle_y, margin + max_width, subtitle_y + 5), radius=3, fill=PINK)
        subtitle_lines = subtitle.split("\n")
        for index, line in enumerate(subtitle_lines):
            draw.text((margin, subtitle_y + 42 + index * 50), line, font=font(27), fill=MUTED)
    else:
        title_size = 79 if not final else 70
        title_y = 350 if not final else 300
        lines = title.split("\n")
        for index, line in enumerate(lines):
            draw.text((margin, title_y + index * 98), line, font=font(title_size, True), fill=WHITE)
        subtitle_y = title_y + len(lines) * 104 + 45
        draw.rounded_rectangle((margin, subtitle_y, width - margin, subtitle_y + 6), radius=3, fill=PINK)
        for index, line in enumerate(subtitle.split("\n")):
            draw.text((margin, subtitle_y + 45 + index * 48), line, font=font(27), fill=MUTED)

    if final:
        chips = [("一句话", BLUE), ("可编辑 AE", PINK), ("动效交付", TEAL), ("MIT 开源计划", WHITE)]
        x = margin
        y = height - (235 if width <= 1080 else 170)
        for label, color in chips:
            text_box = draw.textbbox((0, 0), label, font=font(21, True))
            chip_width = text_box[2] - text_box[0] + 44
            if x + chip_width > width - margin:
                x = margin
                y += 60
            draw.rounded_rectangle((x, y, x + chip_width, y + 44), radius=6, outline=color, width=2)
            draw.text((x + 22, y + 8), label, font=font(21, True), fill=color)
            x += chip_width + 18
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def make_vertical_overlay(work: Path) -> Path:
    image = Image.new("RGBA", (1080, 1440), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((56, 68), "一句话 → 可编辑 AE → 动效交付", font=font(45, True), fill=WHITE)
    draw.text((58, 138), "MotionPilot + MotionSheet = MotionHub", font=font(25), fill=TEAL)
    draw.line((56, 202, 1024, 202), fill=LINE, width=2)
    draw.text((56, 1120), "MotionPilot + MotionSheet = MotionHub", font=font(29, True), fill=WHITE)
    draw.text((56, 1172), "真实屏幕录制；等待段有标注压缩，生成与解析过程保持原速", font=font(23), fill=MUTED)
    draw.text((56, 1260), "MotionPilot 写回关键帧", font=font(24, True), fill=PINK)
    draw.text((430, 1260), "MotionSheet 读成交付表", font=font(24, True), fill=TEAL)
    draw.text((56, 1322), "ZERB LION / 2026", font=font(20, True), fill=MUTED)
    output = work / "vertical-overlay.png"
    image.save(output)
    return output


def build_clean_capture(raw: Path, output: Path) -> None:
    # 33-68 seconds is the uninterrupted real interaction. The API wait is 2x
    # to keep the launch film moving while preserving the authentic UI states.
    graph = (
        "[0:v]crop=2868:1614:70:30,scale=1920:1080:flags=lanczos,split=4[v0][v1][v2][v3];"
        "[v0]trim=start=33:end=40,setpts=PTS-STARTPTS[a0];"
        "[v1]trim=start=40:end=48,setpts=0.5*(PTS-STARTPTS)[a1];"
        "[v2]trim=start=48:end=56,setpts=PTS-STARTPTS[a2];"
        "[v3]trim=start=56:end=68,setpts=PTS-STARTPTS[a3];"
        "[a0][a1][a2][a3]concat=n=4:v=1:a=0,fps=30,format=yuv420p[out]"
    )
    run(
        FFMPEG,
        "-y",
        "-i",
        raw,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        output,
    )


def build_widget_capture(raw: Path, output: Path) -> None:
    graph = (
        "[0:v]trim=start=5,setpts=PTS-STARTPTS,"
        "crop=trunc(ih*16/9/2)*2:ih:(iw-ow)/2:0,"
        "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p[out]"
    )
    run(
        FFMPEG,
        "-y",
        "-i",
        raw,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-movflags",
        "+faststart",
        output,
    )


def encode_ae_segment(
    source: Path,
    overlays: list[Path],
    focus_overlays: list[Path],
    output: Path,
) -> None:
    zoom = (
        "if(lt(on,24),1+0.9*(0.5-0.5*cos(PI*on/24)),"
        "if(lt(on,165),1.9,"
        "if(lt(on,195),1.9-0.45*(0.5-0.5*cos(PI*(on-165)/30)),"
        "if(lt(on,246),1.45,"
        "if(lt(on,276),1.45+0.45*(0.5-0.5*cos(PI*(on-246)/30)),"
        "if(lt(on,360),1.9,"
        "if(lt(on,390),1.9-0.9*(0.5-0.5*cos(PI*(on-360)/30)),1)))))))"
    )
    move_to_timeline = "0.5-0.5*cos(PI*(on-246)/30)"
    return_to_full = "0.5-0.5*cos(PI*(on-360)/30)"
    timeline_x = "1380-iw/(2*zoom)"
    timeline_y = "ih-ih/zoom"
    center_x = "(iw-iw/zoom)/2"
    center_y = "(ih-ih/zoom)/2"
    x = (
        "if(lt(on,246),iw-iw/zoom,"
        f"if(lt(on,276),(iw-iw/zoom)*(1-({move_to_timeline}))+"
        f"({timeline_x})*({move_to_timeline}),"
        f"if(lt(on,360),{timeline_x},"
        f"if(lt(on,390),({timeline_x})*(1-({return_to_full}))+"
        f"({center_x})*({return_to_full}),{center_x}))))"
    )
    input_y = "490-ih/(2*zoom)"
    y = (
        f"if(lt(on,246),max(0,min(ih-ih/zoom,{input_y})),"
        f"if(lt(on,276),max(0,min(ih-ih/zoom,{input_y}))*(1-({move_to_timeline}))+"
        f"({timeline_y})*({move_to_timeline}),"
        f"if(lt(on,360),{timeline_y},"
        f"if(lt(on,390),({timeline_y})*(1-({return_to_full}))+"
        f"({center_y})*({return_to_full}),{center_y}))))"
    )
    graph = (
        "[1:v]format=rgba,fade=t=in:st=0:d=0.35:alpha=1,"
        "fade=t=out:st=5.65:d=0.35:alpha=1[t1];"
        "[2:v]format=rgba,fade=t=in:st=6:d=0.30:alpha=1,"
        "fade=t=out:st=7.90:d=0.30:alpha=1[t2];"
        "[3:v]format=rgba,fade=t=in:st=8.2:d=0.35:alpha=1,"
        "fade=t=out:st=19.65:d=0.35:alpha=1[t3];"
        "[4:v]format=rgba,fade=t=in:st=0:d=0.45:alpha=1,"
        "fade=t=out:st=5.55:d=0.45:alpha=1[g1];"
        "[5:v]format=rgba,fade=t=in:st=6:d=0.35:alpha=1,"
        "fade=t=out:st=7.85:d=0.35:alpha=1[g2];"
        "[6:v]format=rgba,fade=t=in:st=8.2:d=0.40:alpha=1,"
        "fade=t=out:st=11.60:d=0.40:alpha=1[g3];"
        "[7:v]format=rgba,fade=t=in:st=12:d=0.45:alpha=1,"
        "fade=t=out:st=19.55:d=0.45:alpha=1[g4];"
        "[0:v]split=3[s0][s1][s2];"
        "[s0]trim=start=0:end=6,setpts=PTS-STARTPTS[p0];"
        "[s1]trim=start=6:end=19,setpts=(PTS-STARTPTS)/6[p1];"
        "[s2]trim=start=19:end=30.9,setpts=PTS-STARTPTS[p2];"
        "[p0][p1][p2]concat=n=3:v=1:a=0,fps=30[cut];"
        f"[cut]zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1920x1080:fps=30[base];"
        "[base][t1]overlay=0:0:shortest=1:enable='between(t,0,6)'[v1];"
        "[v1][t2]overlay=0:0:shortest=1:enable='between(t,6,8.2)'[v2];"
        "[v2][t3]overlay=0:0:shortest=1:enable='between(t,8.2,20.2)'[v3];"
        "[v3][g1]overlay=0:0:shortest=1:enable='between(t,0,6)'[f1];"
        "[f1][g2]overlay=0:0:shortest=1:enable='between(t,6,8.2)'[f2];"
        "[f2][g3]overlay=0:0:shortest=1:enable='between(t,8.2,12)'[f3];"
        "[f3][g4]overlay=0:0:shortest=1:enable='between(t,12,20.2)',"
        "fps=30,format=yuv420p[out]"
    )
    args: list[object] = [FFMPEG, "-y", "-i", source]
    for overlay in [*overlays, *focus_overlays]:
        args.extend(["-loop", "1", "-framerate", "30", "-i", overlay])
    args.extend(
        [
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "15",
            "-movflags",
            "+faststart",
            output,
        ]
    )
    run(*args)


def encode_widget_segment(
    source: Path,
    overlays: list[Path],
    focus_overlays: list[Path],
    output: Path,
) -> None:
    segment_end = max(5.5, duration(source) - 8.0)
    move_to_progress = "0.5-0.5*cos(PI*(on-90)/30)"
    move_to_result = "0.5-0.5*cos(PI*(on-150)/30)"
    move_to_handle = "0.5-0.5*cos(PI*(on-222)/24)"
    zoom = (
        "if(lt(on,24),1+0.55*(0.5-0.5*cos(PI*on/24)),"
        "if(lt(on,150),1.55,"
        "if(lt(on,180),1.55-0.10*(0.5-0.5*cos(PI*(on-150)/30)),"
        "if(lt(on,222),1.45,"
        "if(lt(on,246),1.45+0.10*(0.5-0.5*cos(PI*(on-222)/24)),1.55)))))"
    )
    right_x = "iw-iw/zoom"
    result_x = "1100-iw/(2*zoom)"
    input_y = "max(0,min(ih-ih/zoom,760-ih/(2*zoom)))"
    progress_y = "0"
    result_y = "max(0,min(ih-ih/zoom,620-ih/(2*zoom)))"
    x = (
        f"if(lt(on,150),{right_x},"
        f"if(lt(on,180),({right_x})*(1-({move_to_result}))+"
        f"({result_x})*({move_to_result}),"
        f"if(lt(on,222),{result_x},"
        f"if(lt(on,246),({result_x})*(1-({move_to_handle})),0))))"
    )
    y = (
        f"if(lt(on,90),{input_y},"
        f"if(lt(on,120),({input_y})*(1-({move_to_progress}))+"
        f"({progress_y})*({move_to_progress}),"
        f"if(lt(on,150),{progress_y},"
        f"if(lt(on,180),({progress_y})*(1-({move_to_result}))+"
        f"({result_y})*({move_to_result}),"
        f"if(lt(on,222),{result_y},"
        f"if(lt(on,246),({result_y})*(1-({move_to_handle})),0))))))"
    )
    graph = (
        f"[1:v]fade=t=in:st=0:d=0.35:alpha=1,"
        f"fade=t=out:st=2.65:d=0.35:alpha=1[t1];"
        f"[2:v]fade=t=in:st=3:d=0.30:alpha=1,"
        f"fade=t=out:st=4.70:d=0.30:alpha=1[t2];"
        f"[3:v]fade=t=in:st=5:d=0.35:alpha=1,"
        f"fade=t=out:st=7.20:d=0.40:alpha=1[t3];"
        f"[4:v]fade=t=in:st=0:d=0.45:alpha=1,"
        f"fade=t=out:st=2.55:d=0.45:alpha=1[g1];"
        f"[5:v]fade=t=in:st=3:d=0.35:alpha=1,"
        f"fade=t=out:st=4.65:d=0.35:alpha=1[g2];"
        f"[6:v]fade=t=in:st=5:d=0.40:alpha=1,"
        f"fade=t=out:st=7.20:d=0.40:alpha=1[g3];"
        f"[7:v]fade=t=in:st=7.60:d=0.45:alpha=1,"
        f"fade=t=out:st={segment_end - 0.45:.3f}:d=0.45:alpha=1[g4];"
        "[0:v]split=3[s0][s1][s2];"
        "[s0]trim=start=0:end=3,setpts=PTS-STARTPTS[p0];"
        "[s1]trim=start=3:end=13,setpts=(PTS-STARTPTS)/5[p1];"
        "[s2]trim=start=13,setpts=PTS-STARTPTS[p2];"
        "[p0][p1][p2]concat=n=3:v=1:a=0,fps=30[cut];"
        f"[cut]zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1920x1080:fps=30[base];"
        "[base][t1]overlay=0:0:shortest=1:enable='between(t,0,3)'[v1];"
        "[v1][t2]overlay=0:0:shortest=1:enable='between(t,3,5)'[v2];"
        "[v2][t3]overlay=0:0:shortest=1:enable='between(t,5,7.6)'[v3];"
        "[v3][g1]overlay=0:0:shortest=1:enable='between(t,0,3)'[f1];"
        "[f1][g2]overlay=0:0:shortest=1:enable='between(t,3,5)'[f2];"
        "[f2][g3]overlay=0:0:shortest=1:enable='between(t,5,7.6)'[f3];"
        f"[f3][g4]overlay=0:0:shortest=1:enable='between(t,7.6,{segment_end:.3f})',"
        "fps=30,format=yuv420p[out]"
    )
    args: list[object] = [FFMPEG, "-y", "-i", source]
    for overlay in [*overlays, *focus_overlays]:
        args.extend(["-loop", "1", "-framerate", "30", "-i", overlay])
    args.extend(
        [
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "15",
            "-movflags",
            "+faststart",
            output,
        ]
    )
    run(*args)


def encode_sheet_segment(gif: Path, overlays: list[Path], output: Path) -> None:
    graph = (
        "[1:v]fade=t=in:st=0:d=0.35:alpha=1,"
        "fade=t=out:st=4.65:d=0.35:alpha=1[t1];"
        "[2:v]fade=t=in:st=5:d=0.35:alpha=1,"
        "fade=t=out:st=9.65:d=0.35:alpha=1[t2];"
        "[3:v]fade=t=in:st=10:d=0.35:alpha=1,"
        "fade=t=out:st=14.32:d=0.35:alpha=1[t3];"
        "[0:v]fps=30,scale=1920:-2:flags=lanczos,"
        "pad=1920:1080:0:(oh-ih)/2:color=0x05070c[base];"
        "[base][t1]overlay=0:0:shortest=1:enable='between(t,0,5)'[v1];"
        "[v1][t2]overlay=0:0:shortest=1:enable='between(t,5,10)'[v2];"
        "[v2][t3]overlay=0:0:shortest=1:enable='between(t,10,14.7)',"
        "fps=30,format=yuv420p[out]"
    )
    args: list[object] = [FFMPEG, "-y", "-i", gif]
    for overlay in overlays:
        args.extend(["-loop", "1", "-framerate", "30", "-i", overlay])
    args.extend(
        [
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-t",
            "14.67",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "15",
            "-movflags",
            "+faststart",
            output,
        ]
    )
    run(*args)


def encode_extra_sheet_segment(
    source: Path,
    overlays: list[Path],
    output: Path,
) -> None:
    graph = (
        "[1:v]fade=t=in:st=0:d=0.35:alpha=1,"
        "fade=t=out:st=3.65:d=0.35:alpha=1[t1];"
        "[2:v]fade=t=in:st=4:d=0.35:alpha=1,"
        "fade=t=out:st=7.65:d=0.35:alpha=1[t2];"
        "[3:v]fade=t=in:st=8:d=0.35:alpha=1,"
        "fade=t=out:st=11.65:d=0.35:alpha=1[t3];"
        "[0:v]fps=30,format=yuv420p[base];"
        "[base][t1]overlay=0:0:shortest=1:enable='between(t,0,4)'[v1];"
        "[v1][t2]overlay=0:0:shortest=1:enable='between(t,4,8)'[v2];"
        "[v2][t3]overlay=0:0:shortest=1:enable='between(t,8,12)',"
        "fps=30,format=yuv420p[out]"
    )
    args: list[object] = [FFMPEG, "-y", "-i", source]
    for overlay in overlays:
        args.extend(["-loop", "1", "-framerate", "30", "-i", overlay])
    args.extend(
        [
            "-filter_complex",
            graph,
            "-map",
            "[out]",
            "-t",
            "12",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "15",
            "-movflags",
            "+faststart",
            output,
        ]
    )
    run(*args)


def encode_summary_segment(
    ae_result: Path,
    gif: Path,
    overlay: Path,
    output: Path,
) -> None:
    graph = (
        "[0:v]fps=30,crop=1080:1080:420:0,scale=960:960:flags=lanczos,"
        "pad=960:1080:0:60:color=0x05070c[ae];"
        "[1:v]fps=30,split=2[sbg][sfg];"
        "[sbg]scale=960:1080:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=960:1080,gblur=sigma=34,eq=brightness=-0.55:saturation=0.5[sheet-bg];"
        "[sfg]scale=920:-2:flags=lanczos[sheet-fg];"
        "[sheet-bg][sheet-fg]overlay=20:(H-h)/2[sheet];"
        "[ae][sheet]hstack=inputs=2,"
        "drawbox=x=958:y=0:w=4:h=1080:color=0x263044@0.9:t=fill[base];"
        "[2:v]fade=t=in:st=0:d=0.35:alpha=1,"
        "fade=t=out:st=3.65:d=0.35:alpha=1[title];"
        "[base][title]overlay=0:0:shortest=1,fps=30,format=yuv420p[out]"
    )
    run(
        FFMPEG,
        "-y",
        "-stream_loop",
        "-1",
        "-i",
        ae_result,
        "-stream_loop",
        "-1",
        "-i",
        gif,
        "-loop",
        "1",
        "-framerate",
        "30",
        "-i",
        overlay,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-t",
        "4",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "15",
        "-movflags",
        "+faststart",
        output,
    )


def encode_vertical_segment(source: Path, overlay: Path, output: Path) -> None:
    graph = (
        "[0:v]scale=1080:608:flags=lanczos,pad=1080:1440:0:250:color=0x05070c[base];"
        "[base][1:v]overlay=0:0,format=yuv420p[out]"
    )
    run(
        FFMPEG,
        "-y",
        "-i",
        source,
        "-i",
        overlay,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "16",
        "-movflags",
        "+faststart",
        output,
    )


def encode_still(image: Path, seconds: float, output: Path) -> None:
    run(
        FFMPEG,
        "-y",
        "-loop",
        "1",
        "-i",
        image,
        "-t",
        f"{seconds:.2f}",
        "-vf",
        "fps=30,format=yuv420p",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        output,
    )


def crossfade_video_segments(
    first: Path,
    second: Path,
    output: Path,
    seconds: float = 0.35,
) -> None:
    offset = max(0.0, duration(first) - seconds)
    graph = (
        f"[0:v][1:v]xfade=transition=fade:duration={seconds:.2f}:"
        f"offset={offset:.3f},fps=30,format=yuv420p[out]"
    )
    run(
        FFMPEG,
        "-y",
        "-i",
        first,
        "-i",
        second,
        "-filter_complex",
        graph,
        "-map",
        "[out]",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "16",
        "-movflags",
        "+faststart",
        output,
    )


def concat_with_silent_audio(segments: list[Path], output: Path, work: Path) -> None:
    concat_file = work / f"{output.stem}-concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{path.as_posix()}'" for path in segments) + "\n",
        encoding="utf-8",
    )
    run(
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-f",
        "lavfi",
        "-i",
        "anullsrc=channel_layout=stereo:sample_rate=48000",
        "-shortest",
        "-vf",
        "fps=30,format=yuv420p",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "16",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        output,
    )


def make_covers(source: Path, work: Path) -> None:
    frame_path = work / "ae-cover-frame.png"
    run(FFMPEG, "-y", "-ss", "27.5", "-i", source, "-frames:v", "1", frame_path)
    shutil.copy2(frame_path, POST / "ae-motionpilot.png")

    base = Image.open(frame_path).convert("RGB")
    cover = base.copy().convert("RGBA")
    shade = Image.new("RGBA", cover.size, (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    shade_draw.rectangle((0, 0, 1920, 270), fill=(0, 0, 0, 185))
    shade_draw.rectangle((0, 860, 1920, 1080), fill=(0, 0, 0, 140))
    cover.alpha_composite(shade)
    draw = ImageDraw.Draw(cover)
    draw.text((70, 42), "手K动效已死？", font=font(66, True), fill=WHITE)
    draw.text((70, 128), "AI 正在接管 AE", font=font(66, True), fill=TEAL)
    draw.text((72, 890), "右侧一句话  →  左侧可编辑关键帧  →  JSON 动效交付", font=font(30, True), fill=WHITE)
    draw.text((72, 950), "MOTIONPILOT + MOTIONSHEET = MOTIONHUB", font=font(23, True), fill=PINK)
    cover.convert("RGB").save(POST / "cover.png", quality=95)

    social = Image.new("RGB", (1080, 1440), BG)
    social_draw = ImageDraw.Draw(social)
    social_draw.text((58, 64), "手K动效已死？", font=font(68, True), fill=WHITE)
    social_draw.text((58, 154), "AI 正在接管 AE", font=font(68, True), fill=TEAL)
    social_draw.text((60, 250), "一句话生成可编辑关键帧", font=font(29, True), fill=PINK)
    fitted = base.resize((1080, 608), Image.Resampling.LANCZOS)
    social.paste(fitted, (0, 350))
    social_draw.line((58, 1015, 1022, 1015), fill=LINE, width=2)
    social_draw.text((58, 1060), "MotionPilot", font=font(38, True), fill=WHITE)
    social_draw.text((332, 1068), "把自然语言写回 After Effects", font=font(25), fill=MUTED)
    social_draw.text((58, 1140), "MotionSheet", font=font(38, True), fill=WHITE)
    social_draw.text((332, 1148), "把 JSON 变成动效交付表", font=font(25), fill=MUTED)
    social_draw.text((58, 1308), "MOTIONHUB / MIT 开源计划", font=font(27, True), fill=TEAL)
    social.save(POST / "social-cover.png", quality=95)


def build(raw: Path | None, widget_raw: Path | None) -> None:
    if not FFMPEG or not FFPROBE:
        raise RuntimeError("ffmpeg and ffprobe must be available on PATH")
    if not FONT_BOLD.exists() or not FONT_REGULAR.exists():
        raise RuntimeError("Microsoft YaHei fonts are required")

    POST.mkdir(parents=True, exist_ok=True)
    clean = POST / "ae-motionpilot-live.mp4"
    if raw:
        if not raw.exists():
            raise FileNotFoundError(raw)
        build_clean_capture(raw, clean)
    elif not clean.exists():
        raise FileNotFoundError("Pass --raw for the first build; cleaned AE source is missing")

    widget = POST / "ae-widget-live.mp4"
    if widget_raw:
        if not widget_raw.exists():
            raise FileNotFoundError(widget_raw)
        build_widget_capture(widget_raw, widget)
    elif not widget.exists():
        raise FileNotFoundError(
            "Pass --widget-raw for the first build; cleaned widget source is missing"
        )

    sheet_gif = POST / "motionsheet-demo.gif"
    if not sheet_gif.exists():
        raise FileNotFoundError(sheet_gif)
    extra_sheet = POST / "motionsheet-extra-demo.mp4"
    if not extra_sheet.exists():
        raise FileNotFoundError(extra_sheet)

    with tempfile.TemporaryDirectory(prefix="motionhub-launch-") as tmp:
        work = Path(tmp)
        ae_overlays = make_horizontal_overlays(work)
        ae_focus_overlays = make_ae_focus_overlays(work)
        widget_overlays = make_widget_overlays(work)
        widget_focus_overlays = make_widget_focus_overlays(work)
        sheet_overlays = make_sheet_overlays(work)
        extra_sheet_overlays = make_extra_sheet_overlays(work)
        summary_overlay = make_summary_overlay(work)
        vertical_ae_overlay = make_vertical_overlay(work)

        ae_h = work / "ae-h.mp4"
        widget_h = work / "widget-h.mp4"
        ae_chain_h = work / "ae-chain-h.mp4"
        sheet_h = work / "sheet-h.mp4"
        extra_sheet_h = work / "sheet-extra-h.mp4"
        summary_h = work / "summary-h.mp4"
        encode_ae_segment(clean, ae_overlays, ae_focus_overlays, ae_h)
        encode_widget_segment(
            widget,
            widget_overlays,
            widget_focus_overlays,
            widget_h,
        )
        crossfade_video_segments(ae_h, widget_h, ae_chain_h)
        encode_sheet_segment(sheet_gif, sheet_overlays, sheet_h)
        encode_extra_sheet_segment(
            extra_sheet,
            extra_sheet_overlays,
            extra_sheet_h,
        )
        encode_summary_segment(
            POST / "ae-motion-result.mp4",
            sheet_gif,
            summary_overlay,
            summary_h,
        )
        horizontal = POST / "motionhub-demo.mp4"
        concat_with_silent_audio(
            [ae_chain_h, sheet_h, extra_sheet_h, summary_h],
            horizontal,
            work,
        )

        encode_vertical_segment(
            horizontal,
            vertical_ae_overlay,
            POST / "motionhub-demo-vertical.mp4",
        )

        make_covers(clean, work)

    print(f"horizontal={duration(POST / 'motionhub-demo.mp4'):.2f}s")
    print(f"vertical={duration(POST / 'motionhub-demo-vertical.mp4'):.2f}s")
    print(f"clean_ae={duration(clean):.2f}s")
    print(f"clean_widget={duration(widget):.2f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the MotionHub launch videos and covers")
    parser.add_argument(
        "--raw",
        type=Path,
        default=None,
        help="Raw AE screen recording. Omit after ae-motionpilot-live.mp4 has been generated.",
    )
    parser.add_argument(
        "--widget-raw",
        type=Path,
        default=None,
        help="Raw widget AE recording. Omit after ae-widget-live.mp4 has been generated.",
    )
    args = parser.parse_args()
    build(args.raw, args.widget_raw)


if __name__ == "__main__":
    main()
