
import csv, os, argparse
from typing import Dict, List
from renderer import render_card
from gemini_client import fetch_fragrance_data

ROOT = os.path.dirname(__file__)

def _normalize_rows(rows: List[Dict]) -> List[Dict]:
    out = []
    for r in rows:
        out.append({
            "name": r.get("name","").strip(),
            "longevity": r.get("longevity","").strip() or "6–8 HRS",
            "projection": r.get("projection","").strip() or "1–2 FEET",
            "when": [s.strip() for s in (r.get("when","") or "").split(";") if s.strip()] or ["Fall"],
            "where": [s.strip() for s in (r.get("where","") or "").split(";") if s.strip()] or ["Casual"],
            "profile": [s.strip() for s in (r.get("profile","") or "").split(";") if s.strip()] or ["Woody"],
            "notes": [s.strip() for s in (r.get("notes","") or "").split(";") if s.strip()] or ["Cedar"],
            "year": r.get("year","") or "",
            "rating": r.get("rating","") or "",
            "description": r.get("description","") or ""
        })
    return out

def from_csv(csv_path: str) -> List[Dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return _normalize_rows(list(reader))

def from_name(name: str) -> Dict:
    return fetch_fragrance_data(name)

def main():
    parser = argparse.ArgumentParser(description="Fragrance Card Generator")
    parser.add_argument("--name", help="Single fragrance name")
    parser.add_argument("--csv", help="CSV path with multiple fragrances")
    parser.add_argument("--out", help="Output directory", default=os.path.join(ROOT, "out"))
    parser.add_argument("--spec", help="Template spec path", default=os.path.join(ROOT, "template_spec.json"))
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    jobs = []
    if args.csv:
        rows = from_csv(args.csv)
        jobs.extend(rows)
    if args.name:
        jobs.append(from_name(args.name))

    if not jobs:
        parser.error("Provide --name or --csv")

    for job in jobs:
        safe = "".join(c for c in job["name"] if c.isalnum() or c in (" ","-","_")).strip().replace(" ","_")
        out_path = os.path.join(args.out, f"{safe}.png")
        render_card(job, args.spec, out_path)
        print("Saved:", out_path)

if __name__ == "__main__":
    main()
