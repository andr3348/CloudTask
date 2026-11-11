#!/usr/bin/env python3
"""Prepara un subconjunto cats/dogs desde Kaggle PetImages.

Uso:
  uv run --with pillow python prepare_dataset.py --src /tmp/opencode/cv/extracted/PetImages --out data
"""
import argparse, csv, shutil
from pathlib import Path
from PIL import Image

def valid(p: Path) -> bool:
    try:
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            w, h = im.size
            return w >= 100 and h >= 100
    except Exception:
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--train", type=int, default=30)
    ap.add_argument("--test", type=int, default=10)
    a = ap.parse_args()

    src, out = Path(a.src), Path(a.out)
    manifest = []
    for label, folder in [("cats", "Cat"), ("dogs", "Dog")]:
        files = sorted((src / folder).glob("*.jpg"))
        picked = 0
        for split, count in [("train", a.train), ("test", a.test)]:
            dest = out / split / label
            dest.mkdir(parents=True, exist_ok=True)
            got = 0
            while got < count:
                if picked >= len(files):
                    raise SystemExit(f"No hay suficientes imágenes válidas para {label}")
                f = files[picked]; picked += 1
                if not valid(f):
                    continue
                target = dest / f"{label}_{split}_{got:03d}{f.suffix.lower()}"
                shutil.copyfile(f, target)
                manifest.append([split, label, target.name])
                got += 1
            print(f"{split}/{label}: {got} imágenes")
    with open(out / "manifest.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["split", "label", "file"]); w.writerows(manifest)
    print("Total:", len(manifest))

if __name__ == "__main__":
    main()
