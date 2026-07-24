from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "posts" / "2026-07-16-motionhub"

BG = (7, 9, 14)
PANEL = (16, 20, 29)
PANEL_2 = (21, 27, 38)
WHITE = (245, 247, 251)
MUTED = (159, 169, 188)
LINE = (47, 57, 76)
CYAN = (78, 220, 211)
BLUE = (108, 159, 255)
PINK = (255, 91, 158)
AMBER = (255, 190, 89)
GREEN = (129, 226, 137)

FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")
FONT_REGULAR = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_MONO = Path(r"C:\Windows\Fonts\consola.ttf")


def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


def rounded_image(image: Image.Image, size: tuple[int, int], radius: int = 22) -> Image.Image:
    fitted = ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    fitted.putalpha(mask)
    return fitted


def add_glow(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    alpha: int = 58,
    blur: int = 48,
) -> None:
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(box, radius=34, fill=(*color, alpha))
    canvas.alpha_composite(glow.filter(ImageFilter.GaussianBlur(blur)))


def draw_grid(canvas: Image.Image) -> None:
    draw = ImageDraw.Draw(canvas)
    width, height = canvas.size
    for x in range(0, width, 80):
        draw.line((x, 0, x, height), fill=(21, 27, 39, 90), width=1)
    for y in range(0, height, 80):
        draw.line((0, y, width, y), fill=(21, 27, 39, 90), width=1)


def draw_badge(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    color: tuple[int, int, int],
    *,
    size: int = 22,
) -> int:
    x, y = xy
    text_font = font(size, True)
    bounds = draw.textbbox((0, 0), text, font=text_font)
    width = bounds[2] - bounds[0] + 34
    height = bounds[3] - bounds[1] + 24
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=color)
    draw.text((x + 17, y + 8), text, font=text_font, fill=BG)
    return width


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2 - 15, y2), fill=color, width=5)
    draw.polygon(((x2, y2), (x2 - 18, y2 - 11), (x2 - 18, y2 + 11)), fill=color)


def draw_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    phase: str,
    title: str,
    role: str,
    color: tuple[int, int, int],
    source: Image.Image | None,
    crop: tuple[int, int, int, int] | None,
    footer: str,
) -> None:
    x1, y1, x2, y2 = box
    add_glow(canvas, (x1 - 6, y1 - 6, x2 + 6, y2 + 6), color, alpha=30, blur=46)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=26, fill=(*PANEL, 248), outline=(*color, 150), width=2)
    draw.text((x1 + 28, y1 + 25), phase, font=font(20, True), fill=color)
    draw.text((x1 + 28, y1 + 63), title, font=font(41, True), fill=WHITE)
    draw.text((x1 + 28, y1 + 118), role, font=font(22), fill=MUTED)

    image_box = (x1 + 24, y1 + 164, x2 - 24, y2 - 92)
    if source is not None:
        selected = source.crop(crop) if crop else source
        preview = rounded_image(selected, (image_box[2] - image_box[0], image_box[3] - image_box[1]), radius=18)
        canvas.alpha_composite(preview, (image_box[0], image_box[1]))
        draw.rounded_rectangle(image_box, radius=18, outline=(*color, 120), width=2)

    draw.line((x1 + 26, y2 - 70, x2 - 26, y2 - 70), fill=LINE, width=2)
    draw.text((x1 + 28, y2 - 53), footer, font=font(19, True), fill=color)


def draw_token_card(
    canvas: Image.Image,
    box: tuple[int, int, int, int],
    *,
    compact: bool = False,
) -> None:
    x1, y1, x2, y2 = box
    add_glow(canvas, (x1 - 18, y1 - 18, x2 + 18, y2 + 18), AMBER, alpha=64, blur=62)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=26, fill=(*PANEL_2, 252), outline=(*AMBER, 235), width=3)
    draw.text((x1 + 24, y1 + 24), "SHARED CONSTRAINT", font=font(17, True), fill=AMBER)
    draw.text((x1 + 24, y1 + 62), "motion-tokens.json", font=font(26 if compact else 29, True, mono=True), fill=WHITE)
    draw.text((x1 + 24, y1 + 109), "同一份动效规范", font=font(22, True), fill=MUTED)

    rows = [
        ("curve", "easeStandard", CYAN),
        ("duration", "250ms", BLUE),
        ("preset", "slideIn", PINK),
    ]
    row_y = y1 + 161
    row_height = 54 if compact else 82
    for key, value, color in rows:
        draw.rounded_rectangle((x1 + 22, row_y, x2 - 22, row_y + row_height - 12), radius=12, fill=(9, 12, 18), outline=LINE, width=1)
        draw.text((x1 + 39, row_y + (8 if compact else 16)), key, font=font(14 if compact else 16, True, mono=True), fill=MUTED)
        draw.text((x1 + 39, row_y + (25 if compact else 38)), value, font=font(17 if compact else 19, True, mono=True), fill=color)
        row_y += row_height

    footer_y = y2 - (62 if compact else 92)
    draw.line((x1 + 24, footer_y, x2 - 24, footer_y), fill=LINE, width=2)
    draw.text((x1 + 24, footer_y + 22), "不是文件中转，而是共同标准", font=font(17, True), fill=AMBER)


def build_horizontal(spec: Image.Image, pilot: Image.Image, sheet: Image.Image, output: Path) -> None:
    canvas = Image.new("RGBA", (2400, 1350), (*BG, 255))
    draw_grid(canvas)
    add_glow(canvas, (760, 215, 1630, 1180), CYAN, alpha=22, blur=120)
    draw = ImageDraw.Draw(canvas)

    badge_width = draw_badge(draw, (72, 58), "MOTIONHUB / SYSTEM MAP", CYAN, size=20)
    draw.text((72 + badge_width + 24, 66), "真实产品界面 / 当前能力边界", font=font(18, True), fill=MUTED)
    draw.text((72, 132), "一份规范，贯穿生成与交付", font=font(75, True), fill=WHITE)
    draw.text((75, 231), "MotionSpec 定义标准，MotionPilot 在 AE 里执行，MotionSheet 用同一标准交付与走查。", font=font(29), fill=MUTED)

    spec_box = (70, 350, 620, 1048)
    token_box = (662, 410, 1038, 990)
    pilot_box = (1080, 350, 1680, 1048)
    sheet_box = (1722, 350, 2330, 1048)

    spec_crop = (120, 300, min(spec.width, 1220), min(spec.height, 1480))
    pilot_crop = (0, 0, pilot.width, pilot.height)
    sheet_crop = (0, 80, sheet.width, min(sheet.height, 740))

    draw_card(
        canvas,
        spec_box,
        phase="01 / DEFINE",
        title="MotionSpec",
        role="定义曲线、时长与命名预设",
        color=CYAN,
        source=spec,
        crop=spec_crop,
        footer="OUTPUT  →  motion-tokens.json",
    )
    draw_token_card(canvas, token_box)
    draw_card(
        canvas,
        pilot_box,
        phase="02 / BUILD IN AE",
        title="MotionPilot",
        role="一句话规划并写回可编辑关键帧",
        color=PINK,
        source=pilot,
        crop=pilot_crop,
        footer="RESULT  →  editable AE layers & keyframes",
    )
    draw_card(
        canvas,
        sheet_box,
        phase="03 / HANDOFF & AUDIT",
        title="MotionSheet",
        role="把 JSON 变成时间轴、表格与走查",
        color=BLUE,
        source=sheet,
        crop=sheet_crop,
        footer="RESULT  →  table / timeline / audit",
    )

    draw_arrow(draw, (620, 700), (662, 700), AMBER)
    draw_arrow(draw, (1038, 700), (1080, 700), AMBER)
    draw_arrow(draw, (1680, 700), (1722, 700), BLUE)

    draw.rounded_rectangle((70, 1100, 2330, 1278), radius=24, fill=(12, 16, 23), outline=LINE, width=2)
    flow = [
        ("定义", "MotionSpec", CYAN),
        ("约束", "motion-tokens.json", AMBER),
        ("生成", "MotionPilot / AE", PINK),
        ("交付 & 走查", "MotionSheet", BLUE),
    ]
    x = 110
    for index, (label, detail, color) in enumerate(flow):
        draw.text((x, 1130), label, font=font(20, True), fill=color)
        draw.text((x, 1168), detail, font=font(24, True, mono="json" in detail), fill=WHITE)
        if index < len(flow) - 1:
            draw_arrow(draw, (x + 300, 1189), (x + 370, 1189), MUTED)
        x += 530
    draw.text((110, 1232), "当前边界：完整 handoff JSON → MotionPilot → AE 一键闭环仍在迭代。", font=font(18), fill=MUTED)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=96)


def build_vertical(spec: Image.Image, pilot: Image.Image, sheet: Image.Image, output: Path) -> None:
    canvas = Image.new("RGBA", (1080, 1350), (*BG, 255))
    draw_grid(canvas)
    add_glow(canvas, (250, 220, 920, 1260), PINK, alpha=22, blur=110)
    draw = ImageDraw.Draw(canvas)

    draw_badge(draw, (54, 50), "MOTIONHUB / 一张图看懂", CYAN, size=18)
    draw.text((54, 112), "一份规范，贯穿", font=font(58, True), fill=WHITE)
    draw.text((54, 184), "AE 生成与交付走查", font=font(58, True), fill=WHITE)
    draw.text((57, 265), "定义 → 约束 → 生成 → 验证", font=font(25, True), fill=MUTED)

    spec_box = (54, 330, 505, 724)
    token_box = (575, 330, 1026, 724)
    pilot_box = (54, 770, 505, 1188)
    sheet_box = (575, 770, 1026, 1188)

    draw_card(
        canvas,
        spec_box,
        phase="01 / DEFINE",
        title="MotionSpec",
        role="定义公司动效标准",
        color=CYAN,
        source=spec,
        crop=(160, 330, min(spec.width, 1200), min(spec.height, 1440)),
        footer="曲线 · 时长 · 预设",
    )
    draw_token_card(canvas, token_box, compact=True)
    draw_card(
        canvas,
        pilot_box,
        phase="02 / BUILD",
        title="MotionPilot",
        role="一句话写回 AE",
        color=PINK,
        source=pilot,
        crop=(0, 0, pilot.width, pilot.height),
        footer="可编辑图层与关键帧",
    )
    draw_card(
        canvas,
        sheet_box,
        phase="03 / VERIFY",
        title="MotionSheet",
        role="交付与走查",
        color=BLUE,
        source=sheet,
        crop=(0, 80, sheet.width, min(sheet.height, 720)),
        footer="表格 · 时间轴 · 合规检查",
    )

    draw_arrow(draw, (505, 527), (575, 527), AMBER)
    draw.line((800, 724, 800, 745), fill=AMBER, width=5)
    draw.line((800, 745, 280, 745), fill=AMBER, width=5)
    draw.polygon(((280, 770), (266, 746), (294, 746)), fill=AMBER)
    draw_arrow(draw, (505, 980), (575, 980), BLUE)

    draw.rounded_rectangle((54, 1226, 1026, 1304), radius=18, fill=(12, 16, 23), outline=LINE, width=2)
    draw.text((77, 1249), "完整 handoff → AE 一键闭环仍在迭代", font=font(22, True), fill=MUTED)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output, quality=96)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MotionHub system relationship visuals")
    parser.add_argument("--spec-shot", type=Path, required=True)
    parser.add_argument("--sheet-shot", type=Path, required=True)
    parser.add_argument("--pilot-shot", type=Path, default=POST / "ae-motionpilot.png")
    args = parser.parse_args()

    for path in (args.spec_shot, args.sheet_shot, args.pilot_shot):
        if not path.exists():
            raise FileNotFoundError(path)

    POST.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.spec_shot, POST / "motionspec.png")
    shutil.copy2(args.sheet_shot, POST / "motionsheet.png")

    spec = Image.open(args.spec_shot).convert("RGB")
    pilot = Image.open(args.pilot_shot).convert("RGB")
    sheet = Image.open(args.sheet_shot).convert("RGB")

    build_horizontal(spec, pilot, sheet, POST / "motionhub-system.png")
    build_vertical(spec, pilot, sheet, POST / "motionhub-system-vertical.png")
    print(POST / "motionhub-system.png")
    print(POST / "motionhub-system-vertical.png")


if __name__ == "__main__":
    main()
