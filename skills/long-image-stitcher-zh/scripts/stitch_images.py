import argparse
import os
from pathlib import Path

from PIL import Image, ImageColor


def _parse_background(value: str) -> tuple[int, int, int, int]:
    v = (value or "").strip()
    if v.lower() == "transparent":
        return (0, 0, 0, 0)
    rgba = ImageColor.getcolor(v, "RGBA")
    return rgba


def _resample():
    r = getattr(Image, "Resampling", None)
    if r is None:
        return getattr(Image, "LANCZOS", 1)
    return r.LANCZOS


def _compute_offset(container: int, item: int, align: str) -> int:
    if container <= item:
        return 0
    if align == "start":
        return 0
    if align == "end":
        return container - item
    return (container - item) // 2


def stitch_images(
    image_paths: list[Path],
    *,
    direction: str,
    spacing: int,
    align: str,
    normalize: str,
    background: tuple[int, int, int, int],
) -> Image.Image:
    if spacing < 0:
        raise ValueError("spacing must be >= 0")
    if len(image_paths) < 2:
        raise ValueError("at least 2 images are required")

    imgs: list[Image.Image] = []
    for p in image_paths:
        img = Image.open(p)
        imgs.append(img.convert("RGBA"))

    if direction == "vertical":
        target_cross = max(i.width for i in imgs)
        if normalize == "scale":
            scaled: list[Image.Image] = []
            for img in imgs:
                if img.width == target_cross:
                    scaled.append(img)
                    continue
                new_h = max(1, round(img.height * (target_cross / img.width)))
                scaled.append(img.resize((target_cross, new_h), resample=_resample()))
            imgs = scaled

        canvas_w = max(i.width for i in imgs)
        canvas_h = sum(i.height for i in imgs) + spacing * (len(imgs) - 1)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), background)

        y = 0
        for img in imgs:
            x = _compute_offset(canvas_w, img.width, align)
            canvas.alpha_composite(img, (x, y))
            y += img.height + spacing
        return canvas

    if direction == "horizontal":
        target_cross = max(i.height for i in imgs)
        if normalize == "scale":
            scaled = []
            for img in imgs:
                if img.height == target_cross:
                    scaled.append(img)
                    continue
                new_w = max(1, round(img.width * (target_cross / img.height)))
                scaled.append(img.resize((new_w, target_cross), resample=_resample()))
            imgs = scaled

        canvas_h = max(i.height for i in imgs)
        canvas_w = sum(i.width for i in imgs) + spacing * (len(imgs) - 1)
        canvas = Image.new("RGBA", (canvas_w, canvas_h), background)

        x = 0
        for img in imgs:
            y = _compute_offset(canvas_h, img.height, align)
            canvas.alpha_composite(img, (x, y))
            x += img.width + spacing
        return canvas

    raise ValueError("direction must be vertical or horizontal")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--direction",
        required=True,
        choices=["vertical", "horizontal"],
        help="vertical: 竖排拼接；horizontal: 横排拼接",
    )
    p.add_argument(
        "--output",
        required=True,
        help="输出文件路径（建议包含扩展名 .png 或 .jpg）",
    )
    p.add_argument(
        "--spacing",
        type=int,
        default=0,
        help="图片之间的像素间距（默认 0）",
    )
    p.add_argument(
        "--align",
        choices=["start", "center", "end"],
        default="center",
        help="对齐方式：start/center/end（默认 center）",
    )
    p.add_argument(
        "--normalize",
        choices=["pad", "scale"],
        default="pad",
        help="尺寸归一策略：pad 不缩放仅补背景；scale 等比缩放到同一宽/高（默认 pad）",
    )
    p.add_argument(
        "--background",
        default="transparent",
        help='背景色：例如 "#ffffff" 或 "transparent"（默认 transparent）',
    )
    p.add_argument("images", nargs="+", help="输入图片路径，按给定顺序拼接")
    return p.parse_args()


def _save_image(img: Image.Image, output_path: Path, background: tuple[int, int, int, int]) -> None:
    ext = output_path.suffix.lower().lstrip(".")
    if ext in {"jpg", "jpeg"}:
        if background[3] != 255:
            raise ValueError('JPEG 不支持透明背景，请将 --background 设为不透明颜色（如 "#ffffff"）或改用 PNG 输出')
        bg = Image.new("RGB", img.size, background[:3])
        bg.paste(img, mask=img.split()[3])
        bg.save(output_path, format="JPEG", quality=95, optimize=True)
        return

    if ext == "png" or ext == "":
        img.save(output_path, format="PNG")
        return

    img.save(output_path)


def main() -> int:
    args = _parse_args()
    image_paths = [Path(p).expanduser() for p in args.images]
    for p in image_paths:
        if not p.exists():
            raise FileNotFoundError(str(p))

    out = Path(args.output).expanduser()
    if out.parent and not out.parent.exists():
        os.makedirs(out.parent, exist_ok=True)

    bg = _parse_background(args.background)
    stitched = stitch_images(
        image_paths,
        direction=args.direction,
        spacing=args.spacing,
        align=args.align,
        normalize=args.normalize,
        background=bg,
    )
    _save_image(stitched, out, bg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

