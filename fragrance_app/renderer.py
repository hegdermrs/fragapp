
from PIL import Image, ImageDraw, ImageFont
import textwrap, json, os
from typing import Dict, List, Tuple

def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

def _draw_wrapped(draw, text, xy, font, fill, max_width, line_spacing=4):
    x, y = xy
    words = text.split()
    line = ""
    for word in words:
        test = line + (" " if line else "") + word
        w = draw.textlength(test, font=font)
        if w <= max_width:
            line = test
        else:
            draw.text((x, y), line, font=font, fill=fill)
            y += font.size + line_spacing
            line = word
    if line:
        draw.text((x, y), line, font=font, fill=fill)
    return y

def render_card(data: Dict, spec_path: str, out_path: str):
    with open(spec_path, "r") as f:
        spec = json.load(f)
    layout, colors, fonts = spec["layout"], spec["colors"], spec["fonts"]
    img = Image.open(os.path.join(os.path.dirname(spec_path), spec["canvas"]["template_path"])).convert("RGBA")
    draw = ImageDraw.Draw(img)

    f_head = _load_font(fonts["headline"]["path"], fonts["headline"]["size"])
    f_sub  = _load_font(fonts["subhead"]["path"], fonts["subhead"]["size"])
    f_body = _load_font(fonts["body"]["path"], fonts["body"]["size"])
    f_small= _load_font(fonts["small"]["path"], fonts["small"]["size"])

    # Title with accent first word
    title = data["name"].upper()
    accent_words = layout["title"].get("accent_words", 1)
    parts = title.split()
    accent = " ".join(parts[:accent_words])
    rest = " ".join(parts[accent_words:])
    x, y = layout["title"]["xy"]
    draw.text((x, y), accent, font=f_head, fill=colors["accent"])
    ax = x + draw.textlength(accent + " ", font=f_head)
    draw.text((ax, y), rest, font=f_head, fill=colors["primary"])

    # Longevity & Projection
    draw.text(tuple(layout["longevity_header"]["xy"]), layout["longevity_header"]["text"], font=f_sub, fill=colors["accent"])
    draw.text(tuple(layout["longevity_value"]["xy"]), data["longevity"], font=f_head, fill=colors["primary"])

    draw.text(tuple(layout["projection_header"]["xy"]), layout["projection_header"]["text"], font=f_sub, fill=colors["accent"])
    draw.text(tuple(layout["projection_value"]["xy"]), data["projection"], font=f_head, fill=colors["primary"])

    draw.line([tuple(layout["divider"]["xy"]), tuple(layout["divider"]["to"])], fill=colors["primary"], width=2)

    _draw_wrapped(draw, data["description"], tuple(layout["description"]["xy"]), f_body, colors["primary"], layout["description"]["max_width"], layout["description"].get("line_spacing", 6))

    draw.text(tuple(layout["year"]["xy"]), layout["year"]["label"] + str(data["year"]), font=f_small, fill=colors["primary"])
    draw.text(tuple(layout["rating"]["xy"]), layout["rating"]["label"] + str(data["rating"]), font=f_small, fill=colors["primary"])

    rc = layout["right_col"]
    def draw_section(key, header, items):
        draw.text(tuple(rc[key]["header_xy"]), header.upper(), font=f_sub, fill=colors["accent"])
        x, y = rc[key]["list_xy"]
        for i, item in enumerate(items):
            draw.text((x, y + i*rc[key]["items_spacing"]), str(item).title(), font=f_body, fill=colors["primary"])
    draw_section("when", "WHEN", data["when"])
    draw_section("where", "WHERE", data["where"])
    draw_section("profile", "PROFILE", data["profile"])
    draw_section("notes", "NOTES", data["notes"])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path
