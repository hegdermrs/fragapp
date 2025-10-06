
import os, io, csv
import streamlit as st
from PIL import Image
from renderer import render_card
from gemini_client import fetch_fragrance_data

ROOT = os.path.dirname(__file__)
SPEC_PATH = os.path.join(ROOT, "template_spec.json")
OUT_DIR = os.path.join(ROOT, "out")

st.set_page_config(page_title="Fragrance Card Generator", page_icon="🟣", layout="wide")
st.title("🟣 Fragrance Card Generator")

with st.sidebar:
    st.header("Template & Output")
    spec_path = SPEC_PATH
    out_dir = OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    st.write("Template:", os.path.relpath(spec_path, ROOT))
    dpi = st.number_input("Export Scale (1 = 768x768, 2 = 1536x1536)", min_value=1, max_value=4, value=1, step=1)
    export_jpg = st.checkbox("Also export JPG", value=False)

tab1, tab2 = st.tabs(["Single Fragrance", "Batch (CSV)"])

def _safe_name(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in (" ","-","_")).strip().replace(" ","_")

with tab1:
    st.subheader("Single Fragrance")
    name = st.text_input("Fragrance Name", placeholder="Burberry Hero Parfum")
    if st.button("Generate Card", type="primary"):
        if not name.strip():
            st.error("Please enter a name.")
        else:
            data = fetch_fragrance_data(name.strip())
            preview_path = os.path.join(out_dir, f"{_safe_name(data['name'])}.png")
            render_card(data, spec_path, preview_path)
            if dpi > 1:
                img = Image.open(preview_path).convert("RGBA")
                img = img.resize((img.width*dpi, img.height*dpi), Image.LANCZOS)
                img.save(preview_path)
            if export_jpg:
                Image.open(preview_path).convert("RGB").save(preview_path.replace(".png",".jpg"), quality=95)
            st.success(f"Saved: {os.path.basename(preview_path)}")
            st.image(preview_path, caption="Preview", use_column_width=True)
            with open(preview_path, "rb") as f:
                st.download_button("Download PNG", f, file_name=os.path.basename(preview_path))

with tab2:
    st.subheader("Batch from CSV")
    st.caption("Columns: name, longevity, projection, when, where, profile, notes, year, rating, description. Use semicolons for lists.")
    file = st.file_uploader("Upload CSV", type=["csv"])
    if file is not None:
        rows = list(csv.DictReader(io.StringIO(file.getvalue().decode("utf-8"))))
        st.write(f"Detected {len(rows)} rows")
        if st.button("Generate Batch", type="primary"):
            saved = []
            for r in rows:
                job = {
                    "name": r.get("name","").strip(),
                    "longevity": (r.get("longevity","") or "6–8 HRS").strip(),
                    "projection": (r.get("projection","") or "1–2 FEET").strip(),
                    "when": [s.strip() for s in (r.get("when","") or "").split(";") if s.strip()] or ["Fall"],
                    "where": [s.strip() for s in (r.get("where","") or "").split(";") if s.strip()] or ["Casual"],
                    "profile": [s.strip() for s in (r.get("profile","") or "").split(";") if s.strip()] or ["Woody"],
                    "notes": [s.strip() for s in (r.get("notes","") or "").split(";") if s.strip()] or ["Cedar"],
                    "year": r.get("year","") or "",
                    "rating": r.get("rating","") or "",
                    "description": r.get("description","") or ""
                }
                path = os.path.join(out_dir, f"{_safe_name(job['name'])}.png")
                render_card(job, spec_path, path)
                if dpi > 1:
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((img.width*dpi, img.height*dpi), Image.LANCZOS)
                    img.save(path)
                if export_jpg:
                    Image.open(path).convert("RGB").save(path.replace(".png",".jpg"), quality=95)
                saved.append(path)
            st.success(f"Generated {len(saved)} cards.")
            import zipfile, io as iio
            memzip = iio.BytesIO()
            with zipfile.ZipFile(memzip, "w", zipfile.ZIP_DEFLATED) as z:
                for p in saved:
                    z.write(p, arcname=os.path.basename(p))
            memzip.seek(0)
            st.download_button("Download ZIP", memzip, file_name="fragrance_cards.zip")
