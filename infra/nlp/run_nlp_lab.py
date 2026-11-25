#!/usr/bin/env python3
"""Ejecuta las pruebas de Text Analytics y el ciclo completo CLU (sucesor de LUIS) en Azure.

Requiere variables de entorno:
  AZURE_LANG_ENDPOINT, AZURE_LANG_KEY

Uso:
  uv run --with requests python infra/nlp/run_nlp_lab.py
"""
import argparse
import json
import os
import time
from pathlib import Path
import requests

API_VERSION = "2023-04-01"


def req(method: str, url: str, key: str, **kw) -> requests.Response:
    headers = kw.pop("headers", {})
    headers.setdefault("Ocp-Apim-Subscription-Key", key)
    if "json" in kw:
        headers.setdefault("Content-Type", "application/json")
    r = requests.request(method, url, headers=headers, timeout=120, **kw)
    if r.status_code >= 300:
        raise RuntimeError(f"{method} {url} -> {r.status_code}: {r.text[:600]}")
    return r


def poll_operation(op_url: str, key: str, label: str, interval: int = 5) -> dict:
    print(f"  Esperando {label}...")
    while True:
        r = req("GET", op_url, key)
        data = r.json()
        status = data.get("status", "").lower()
        print(f"    estado {label}: {status}")
        if status == "succeeded":
            return data
        if status in ("failed", "cancelled", "canceled"):
            raise RuntimeError(f"Operación {label} fallida: {json.dumps(data, ensure_ascii=False)}")
        time.sleep(interval)


def run_text_analytics(endpoint: str, key: str, samples: list[dict], out_dir: Path) -> dict:
    print("\n=== 1. Azure AI Language: Text Analytics ===")
    url = f"{endpoint}/language/:analyze-text?api-version={API_VERSION}"

    # 1.1 Detección de idioma (todos los textos)
    lang_res = req("POST", url, key, json={
        "kind": "LanguageDetection",
        "analysisInput": {"documents": samples},
    }).json()

    es_docs = [{"id": s["id"], "language": "es", "text": s["text"]} for s in samples if s["id"] in {"1", "2", "3", "4"}]

    # 1.2 Análisis de sentimiento + opinion mining
    sent_res = req("POST", url, key, json={
        "kind": "SentimentAnalysis",
        "parameters": {"opinionMining": True},
        "analysisInput": {"documents": es_docs},
    }).json()

    # 1.3 Reconocimiento de entidades (NER)
    ner_res = req("POST", url, key, json={
        "kind": "EntityRecognition",
        "analysisInput": {"documents": es_docs},
    }).json()

    # 1.4 Extracción de palabras clave
    kp_res = req("POST", url, key, json={
        "kind": "KeyPhraseExtraction",
        "analysisInput": {"documents": es_docs},
    }).json()

    results = {
        "language_detection": lang_res.get("results", {}).get("documents", []),
        "sentiment_analysis": sent_res.get("results", {}).get("documents", []),
        "entity_recognition": ner_res.get("results", {}).get("documents", []),
        "key_phrase_extraction": kp_res.get("results", {}).get("documents", []),
    }
    (out_dir / "text_analytics_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for doc in results["language_detection"]:
        dl = doc["detectedLanguage"]
        print(f"  [Idioma doc {doc['id']}] {dl['name']} ({dl['iso6391Name']}) score={dl['confidenceScore']}")
    for doc in results["sentiment_analysis"]:
        sc = doc["confidenceScores"]
        print(f"  [Sentimiento doc {doc['id']}] {doc['sentiment']} "
              f"(pos={sc['positive']:.2f}, neu={sc['neutral']:.2f}, neg={sc['negative']:.2f})")
    for doc in results["entity_recognition"]:
        ents = [(e["text"], e["category"]) for e in doc["entities"]]
        print(f"  [Entidades doc {doc['id']}] {ents}")
    for doc in results["key_phrase_extraction"]:
        print(f"  [Palabras clave doc {doc['id']}] {doc['keyPhrases']}")

    return results


def chatbot_reply(intent: str, entities: list[dict]) -> str:
    by_cat = {}
    for e in entities:
        by_cat.setdefault(e["category"], []).append(e["text"])
    if intent == "RealizarPedido":
        platos = ", ".join(by_cat.get("Plato", ["tu plato"]))
        srv = f" ({by_cat['TipoServicio'][0]})" if "TipoServicio" in by_cat else ""
        return f"¡Pedido registrado! Prepararemos: {platos}{srv}."
    if intent == "ConsultarMenu":
        return "Menú de hoy: Lomo saltado (S/32), Ceviche mixto (S/35), Pizza familiar (S/45) y Chicha morada (S/10)."
    if intent == "ReservarMesa":
        pers = by_cat.get("NumPersonas", ["los comensales"])[0]
        fh = by_cat.get("FechaHora", ["el horario indicado"])[0]
        return f"Mesa reservada para {pers} ({fh}). ¡Te esperamos!"
    if intent == "ConsultarHorarioUbicacion":
        return "Atendemos de lunes a domingo de 12:00 p. m. a 11:00 p. m. en Av. Larco 450, Miraflores."
    if intent == "CancelarPedido":
        return "Tu pedido ha sido cancelado sin costo. Si deseas ordenar otra cosa, avísanos."
    return "No estoy seguro de entender tu solicitud. Puedo ayudarte a ver el menú, hacer un pedido o reservar una mesa."


def run_clu(endpoint: str, key: str, project_data: dict, holdout: list[dict], out_dir: Path,
            skip_train: bool = False) -> dict:
    print("\n=== 2. Conversational Language Understanding (CLU - sucesor de LUIS) ===")
    project_name = project_data["metadata"]["projectName"]
    base = f"{endpoint}/language/authoring/analyze-conversations/projects/{project_name}"
    model_label = "v1"
    deploy_name = "production"

    if not skip_train:
        # 2.1 Importar proyecto
        print(f"Importando proyecto '{project_name}' ({len(project_data['assets']['utterances'])} frases)...")
        r = req("POST", f"{base}/:import?api-version={API_VERSION}", key, json=project_data)
        poll_operation(r.headers["operation-location"], key, "import")

        # 2.2 Entrenar modelo (español requiere trainingMode="advanced")
        print(f"Entrenando modelo '{model_label}' (advanced, 80% train / 20% test automático)...")
        r = req("POST", f"{base}/:train?api-version={API_VERSION}", key, json={
            "modelLabel": model_label,
            "trainingMode": "advanced",
            "evaluationOptions": {
                "kind": "percentage",
                "trainingSplitPercentage": 80,
                "testingSplitPercentage": 20,
            },
        })
        poll_operation(r.headers["operation-location"], key, "train", interval=10)

    # 2.3 Desplegar modelo (siempre asegura el despliegue actualizado)
    print(f"Desplegando modelo '{model_label}' en '{deploy_name}'...")
    r = req("PUT", f"{base}/deployments/{deploy_name}?api-version={API_VERSION}", key, json={
        "trainedModelLabel": model_label,
    })
    poll_operation(r.headers["operation-location"], key, "deploy", interval=5)

    # 2.4 Resumen de evaluación interna de CLU
    eval_summary = req(
        "GET",
        f"{base}/models/{model_label}/evaluation/summary-result?api-version={API_VERSION}",
        key,
    ).json()
    (out_dir / "clu_eval_summary.json").write_text(
        json.dumps(eval_summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    intents_eval = eval_summary.get("intentsEvaluation", {})
    entities_eval = eval_summary.get("entitiesEvaluation", {})
    print(f"  Evaluación interna CLU -> Intents macro F1: {intents_eval.get('macroF1')}, "
          f"micro F1: {intents_eval.get('microF1')} | Entities micro F1: {entities_eval.get('microF1')}")

    # 2.5 Evaluación hold-out (runtime)
    print(f"\nEvaluando {len(holdout)} frases hold-out contra deployment '{deploy_name}'...")
    runtime_url = f"{endpoint}/language/:analyze-conversations?api-version={API_VERSION}"
    intents_list = [i["category"] for i in project_data["assets"]["intents"]]
    conf = {t: {p: 0 for p in intents_list} for t in intents_list}
    rows = []
    for idx, item in enumerate(holdout, 1):
        res = req("POST", runtime_url, key, json={
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "id": str(idx),
                    "participantId": "cliente1",
                    "modality": "text",
                    "language": "es",
                    "text": item["text"],
                }
            },
            "parameters": {
                "projectName": project_name,
                "deploymentName": deploy_name,
                "verbose": True,
            },
        }).json()
        pred = res["result"]["prediction"]
        top_intent = pred["topIntent"]
        top_score = next((i["confidenceScore"] for i in pred["intents"] if i["category"] == top_intent), 0.0)
        entities = [
            {
                "category": e["category"],
                "text": e["text"],
                "confidenceScore": round(e["confidenceScore"], 4),
            }
            for e in pred.get("entities", [])
        ]
        conf[item["true_intent"]][top_intent] += 1
        reply = chatbot_reply(top_intent, entities)
        ok = item["true_intent"] == top_intent
        rows.append({
            "text": item["text"],
            "true_intent": item["true_intent"],
            "pred_intent": top_intent,
            "confidence": round(top_score, 4),
            "entities": entities,
            "correct": ok,
            "bot_reply": reply,
        })
        print(f"  [{'OK' if ok else 'ERR'}] \"{item['text']}\" -> {top_intent} ({top_score:.4f}) "
              f"| ents={[(e['category'], e['text']) for e in entities]}")

    correct = sum(1 for r in rows if r["correct"])
    accuracy = correct / len(rows)
    print(f"\nHold-out Accuracy: {correct}/{len(rows)} = {accuracy:.1%}")

    # 2.6 Exportar modelo desde Azure
    print("\nExportando proyecto CLU desde Azure Authoring API...")
    r = req("POST", f"{base}/:export?api-version={API_VERSION}&stringIndexType=Utf16CodeUnit", key)
    op = poll_operation(r.headers["operation-location"], key, "export", interval=3)
    if op.get("resultUrl"):
        exported = req("GET", op["resultUrl"], key).json()
    elif op.get("result"):
        exported = op["result"]
    else:
        exported = op
    export_path = out_dir / f"{project_name}-export.json"
    export_path.write_text(json.dumps(exported, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Modelo exportado guardado en: {export_path} ({export_path.stat().st_size} bytes)")

    clu_results = {
        "project_name": project_name,
        "model_label": model_label,
        "deployment_name": deploy_name,
        "train_utterances": len(project_data["assets"]["utterances"]),
        "holdout_total": len(rows),
        "holdout_correct": correct,
        "holdout_accuracy": round(accuracy, 4),
        "confusion_matrix": conf,
        "holdout_predictions": rows,
        "export_file": str(export_path),
    }
    (out_dir / "clu_holdout_results.json").write_text(
        json.dumps(clu_results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return clu_results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="infra/nlp/data")
    ap.add_argument("--out", default="infra/nlp/out")
    ap.add_argument("--skip-train", action="store_true")
    a = ap.parse_args()

    endpoint = os.environ["AZURE_LANG_ENDPOINT"].rstrip("/")
    key = os.environ["AZURE_LANG_KEY"]
    data_dir = Path(a.data)
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    ta_samples = json.loads((data_dir / "text_analytics_samples.json").read_text(encoding="utf-8"))
    project_data = json.loads((data_dir / "clu_restaurant_project.json").read_text(encoding="utf-8"))
    holdout = json.loads((data_dir / "clu_test_holdout.json").read_text(encoding="utf-8"))

    run_text_analytics(endpoint, key, ta_samples, out_dir)
    run_clu(endpoint, key, project_data, holdout, out_dir, skip_train=a.skip_train)


if __name__ == "__main__":
    main()
