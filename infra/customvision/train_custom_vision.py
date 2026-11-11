#!/usr/bin/env python3
"""Entrena, evalúa y exporta un clasificador binario en Azure Custom Vision vía REST.

Requiere variables de entorno:
  CV_TRAIN_ENDPOINT, CV_TRAIN_KEY, CV_PRED_ENDPOINT, CV_PRED_KEY, CV_PROJECT

Uso:
  uv run --with requests python train_custom_vision.py --data data --out out
"""
import argparse, base64, json, os, sys, time
from pathlib import Path
import requests

TRAIN = "customvision/v3.4-preview/training"
PRED = "customvision/v3.0/Prediction"

def hdr(key, name):
    return {name: key, "Content-Type": "application/json"}

def req(method, url, key, key_name, **kw):
    r = requests.request(method, url, headers={key_name: key}, timeout=120, **kw)
    if r.status_code >= 300:
        raise RuntimeError(f"{method} {url} -> {r.status_code}: {r.text[:400]}")
    return r

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--project", default=os.getenv("CV_PROJECT", "hw7-cats-vs-dogs"))
    ap.add_argument("--publish-name", default="hw7-iter1")
    ap.add_argument("--platform", default="ONNX")
    ap.add_argument("--iteration-id", default=None)
    a = ap.parse_args()

    te = os.environ["CV_TRAIN_ENDPOINT"].rstrip("/")
    tk = os.environ["CV_TRAIN_KEY"]
    pe = os.environ["CV_PRED_ENDPOINT"].rstrip("/")
    pk = os.environ["CV_PRED_KEY"]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    data = Path(a.data)

    # 1. Dominio compacto (permite exportar ONNX)
    domains = req("GET", f"{te}/{TRAIN}/domains", tk, "Training-Key").json()
    compact = [d for d in domains if d.get("name") == "General (compact)"]
    dom = compact[0] if compact else next(d for d in domains if d.get("name") == "General")
    print("Dominio:", dom["name"], dom["id"], "exportable:", dom.get("exportable"))

    # 2. Proyecto (reutiliza si ya existe)
    projects = req("GET", f"{te}/{TRAIN}/projects", tk, "Training-Key").json()
    proj = next((p for p in projects if p["name"] == a.project), None)
    if not proj:
        proj = req("POST", f"{te}/{TRAIN}/projects", tk, "Training-Key",
                   params={
                       "name": a.project,
                       "description": "HW7 cats vs dogs - clasificacion de imagenes",
                       "domainId": dom["id"],
                       "classificationType": "Multiclass",
                       "projectType": "Classification",
                       "targetExportPlatforms": a.platform,
                   }).json()
        print("Proyecto creado:", proj["id"])
    else:
        print("Proyecto existente:", proj["id"])
    pid = proj["id"]

    # 3. Etiquetas
    existing = {t["name"]: t["id"] for t in req("GET", f"{te}/{TRAIN}/projects/{pid}/tags", tk, "Training-Key").json()}
    tag_ids = {}
    for name in ("cats", "dogs"):
        if name in existing:
            tag_ids[name] = existing[name]
        else:
            t = req("POST", f"{te}/{TRAIN}/projects/{pid}/tags", tk, "Training-Key", params={"name": name}).json()
            tag_ids[name] = t["id"]
    print("Tags:", tag_ids)

    # 4. Subida de imágenes (batch JSON base64, hasta 64 por request)
    images = req("GET", f"{te}/{TRAIN}/projects/{pid}/images", tk, "Training-Key",
                 params={"take": 200}).json()
    print("Imágenes ya en el proyecto:", len(images))
    uploaded = 0
    if not images:
        for label in ("cats", "dogs"):
            files = sorted((data / "train" / label).glob("*"))
            batch = [{"name": f.name, "contents": base64.b64encode(f.read_bytes()).decode()}
                     for f in files]
            r = req("POST", f"{te}/{TRAIN}/projects/{pid}/images/files", tk, "Training-Key",
                    json={"images": batch, "tagIds": [tag_ids[label]]})
            summary = r.json()
            ok = sum(1 for i in summary.get("images", []) if i.get("status") == "OK")
            print(f"{label}: {ok}/{len(batch)} imágenes aceptadas (batch_ok={summary.get('isBatchSuccessful')})")
            uploaded += ok
    print("Imágenes subidas en esta ejecución:", uploaded)
    total_images = len(req("GET", f"{te}/{TRAIN}/projects/{pid}/images", tk, "Training-Key",
                           params={"take": 200}).json())

    # 5. Entrenamiento rápido (Regular) o reutilización de una iteración existente
    if a.iteration_id:
        iid = a.iteration_id
        it = req("GET", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}", tk, "Training-Key").json()
        print("Iteración existente:", iid, it["status"])
    else:
        it = req("POST", f"{te}/{TRAIN}/projects/{pid}/train", tk, "Training-Key", params={"trainingType": "Regular"}).json()
        iid = it["id"]
        print("Iteración:", iid, it["status"])
        while True:
            it = req("GET", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}", tk, "Training-Key").json()
            print("  estado:", it["status"])
            if it["status"] in ("Completed", "Failed"):
                break
            time.sleep(10)
    if it["status"] != "Completed":
        sys.exit("Entrenamiento fallido")

    # 6. Métricas de la iteración
    perf = req("GET", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}/performance", tk, "Training-Key").json()
    print("Performance:", json.dumps({k: perf.get(k) for k in ("precision", "recall", "averagePrecision")}))

    # 7. Publicar en el recurso de predicción
    prediction_id = os.environ["CV_PREDICTION_ID"]
    try:
        req("POST", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}/publish", tk, "Training-Key",
            params={"publishName": a.publish_name, "predictionId": prediction_id})
        print("Publicado como:", a.publish_name)
    except RuntimeError as ex:
        if "BadRequestIterationIsPublished" in str(ex):
            print("Ya estaba publicado como:", a.publish_name)
        else:
            raise

    # 8. Exactitud sobre el set de prueba (hold-out)
    conf = {"cats": {"cats": 0, "dogs": 0}, "dogs": {"cats": 0, "dogs": 0}}
    rows = []
    for label in ("cats", "dogs"):
        for f in sorted((data / "test" / label).glob("*")):
            r = requests.post(
                f"{pe}/{PRED}/{pid}/classify/iterations/{a.publish_name}/image",
                headers={"Prediction-Key": pk, "Content-Type": "application/octet-stream"},
                data=f.read_bytes(), timeout=120,
            )
            if r.status_code >= 300:
                print("Fallo predicción", f.name, r.status_code, r.text[:150]); continue
            preds = r.json()["predictions"]
            best = max(preds, key=lambda p: p["probability"])
            conf[label][best["tagName"]] += 1
            rows.append({"file": f.name, "true": label, "pred": best["tagName"],
                         "prob": round(best["probability"], 4)})
    n = sum(sum(v.values()) for v in conf.values())
    correct = conf["cats"]["cats"] + conf["dogs"]["dogs"]
    accuracy = correct / n if n else 0
    def pr(tag):
        tp = conf[tag][tag]
        fp = sum(conf[o][tag] for o in conf if o != tag)
        fn = sum(conf[tag][o] for o in conf if o != tag)
        return (tp / (tp + fp) if tp + fp else 0, tp / (tp + fn) if tp + fn else 0)
    p_cat, r_cat = pr("cats"); p_dog, r_dog = pr("dogs")
    print(f"Accuracy hold-out: {accuracy:.4f} ({correct}/{n})")

    # 9. Exportación ONNX
    export_uri = None
    try:
        try:
            req("POST", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}/export", tk, "Training-Key",
                params={"platform": a.platform})
        except RuntimeError as ex:
            if "ExportAlreadyInProgress" not in str(ex):
                raise
            print("Exportación ya en curso; se consulta su estado")
        for _ in range(60):
            e = req("GET", f"{te}/{TRAIN}/projects/{pid}/iterations/{iid}/export", tk, "Training-Key").json()
            items = e if isinstance(e, list) else [e]
            item = next((x for x in items if x.get("platform") == a.platform), items[0] if items else {})
            if item.get("status") == "Done":
                export_uri = item.get("downloadUri"); break
            if item.get("status") == "Failed":
                print("Export status:", item); break
            time.sleep(5)
        if export_uri:
            zip_path = out / f"hw7-cats-vs-dogs-{a.platform.lower()}.zip"
            zip_path.write_bytes(requests.get(export_uri, timeout=300).content)
            print("Exportado:", zip_path, zip_path.stat().st_size, "bytes")
    except Exception as ex:
        print("Exportación no disponible:", ex)

    result = {
        "project_id": pid,
        "iteration_id": iid,
        "publish_name": a.publish_name,
        "domain": dom["name"],
        "trained_images": total_images,
        "custom_vision_metrics": {k: perf.get(k) for k in
            ("precision", "recall", "averagePrecision")},
        "per_tag": perf.get("perTagPerformance", []),
        "holdout": {"n": n, "correct": correct, "accuracy": correct / n if n else 0,
                    "confusion": conf,
                    "precision": {"cats": p_cat, "dogs": p_dog},
                    "recall": {"cats": r_cat, "dogs": r_dog}},
        "predictions": rows,
        "export_platform": a.platform,
        "export_uri": export_uri,
    }
    (out / "results.json").write_text(json.dumps(result, indent=2))
    print("Resultados:", out / "results.json")

if __name__ == "__main__":
    main()
