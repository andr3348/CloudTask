# Implementación HW8 paso a paso (Azure CLI + Azure AI Language REST)

Suscripción **Azure for Students** (`1626065@senati.pe`) · Región **South Central US**.

## 0. Contexto y restricción regional / retiro de LUIS

- La política `sys.regionrestriction` permite desplegar únicamente en `chilecentral`, `northcentralus`,
  `southcentralus`, `canadacentral` y `westus2`.
- El servicio clásico **LUIS** (`LUIS` / `LUIS.Authoring`) fue retirado por Microsoft y ya no dispone de
  SKUs activos en las regiones permitidas. Su sucesor oficial es **Conversational Language Understanding (CLU)**
  dentro de **Azure AI Language** (`kind=TextAnalytics`).
- Un único recurso `TextAnalytics` nivel **F0** en `southcentralus` habilita tanto **Text Analytics** como
  **CLU** (Language Studio / Authoring + Runtime).

## 1. Login y verificación con Azure CLI

```bash
az login --use-device-code
az account set --subscription 463c2b2b-5d7e-4eb5-94d4-908a2e99053e
az provider register --namespace Microsoft.CognitiveServices --wait
```

## 2. Grupo de recursos y recurso Azure AI Language (F0)

```bash
az group create --name rg-cloudtask-hw8 --location southcentralus --tags project=cloudtask-hw8

az cognitiveservices account create \
  --name lang-hw8-4632 \
  --resource-group rg-cloudtask-hw8 \
  --kind TextAnalytics \
  --sku F0 \
  --location southcentralus \
  --custom-domain lang-hw8-4632 \
  --yes \
  --tags project=cloudtask-hw8
```

Obtención de clave y endpoint (guardados localmente en `~/.config/cloudtask/nlp.env`, fuera del repositorio):

```bash
az cognitiveservices account keys list -n lang-hw8-4632 -g rg-cloudtask-hw8 --query key1 -o tsv
az cognitiveservices account show -n lang-hw8-4632 -g rg-cloudtask-hw8 --query properties.endpoint -o tsv
```

## 3. Preparación del dataset y ejecución del laboratorio

El script `infra/nlp/prepare_data.py` genera los conjuntos JSON validando offsets UTF-16:

- `infra/nlp/data/text_analytics_samples.json`: 6 textos (reseñas de restaurante y notas académicas en español, inglés y portugués).
- `infra/nlp/data/clu_restaurant_project.json`: 64 frases etiquetadas en 6 intenciones (`RealizarPedido`, `ConsultarMenu`, `ReservarMesa`, `ConsultarHorarioUbicacion`, `CancelarPedido`, `None`) y 5 entidades (`Plato`, `Cantidad`, `TipoServicio`, `NumPersonas`, `FechaHora`).
- `infra/nlp/data/clu_test_holdout.json`: 18 frases independientes (incluyendo `"Quiero pedir una pizza"` y `"¿Cuál es el menú de hoy?"`).

Ejecución completa (`Text Analytics` + importación, entrenamiento, despliegue, evaluación hold-out y exportación CLU):

```bash
python3 infra/nlp/prepare_data.py
set -a; . ~/.config/cloudtask/nlp.env; set +a
uv run --with requests python infra/nlp/run_nlp_lab.py
```

## 4. Endpoints REST utilizados (`api-version=2023-04-01`)

1. **Text Analytics:** `POST {endpoint}/language/:analyze-text?api-version=2023-04-01` con `kind`: `LanguageDetection`, `SentimentAnalysis` (`opinionMining: true`), `EntityRecognition` y `KeyPhraseExtraction`.
2. **Importación CLU:** `POST {endpoint}/language/authoring/analyze-conversations/projects/hw8-restaurante-luis/:import?api-version=2023-04-01`.
3. **Entrenamiento CLU:** `POST .../hw8-restaurante-luis/:train?api-version=2023-04-01` (`modelLabel: "v1"`, `trainingMode: "advanced"`, split 80/20).
4. **Despliegue CLU:** `PUT .../hw8-restaurante-luis/deployments/production?api-version=2023-04-01` (`trainedModelLabel: "v1"`).
5. **Predicción Runtime:** `POST {endpoint}/language/:analyze-conversations?api-version=2023-04-01`.
6. **Exportación:** `POST .../hw8-restaurante-luis/:export?api-version=2023-04-01&stringIndexType=Utf16CodeUnit`.

## 5. Capturas requeridas para el informe

> Portales: [Azure Portal](https://portal.azure.com) y [Language Studio](https://language.cognitive.azure.com) — iniciar sesión con `1626065@senati.pe` (directorio SENATI) y seleccionar el recurso `lang-hw8-4632`.

1. **Grupo de recursos** `rg-cloudtask-hw8` con el recurso `lang-hw8-4632` (Language, F0, South Central US).
2. **Claves y punto de conexión** de `lang-hw8-4632` (ocultar/mosaicar las claves antes de entregar).
3. **Language Studio → Text Analytics (Analyze text)**: prueba de *Analyze sentiment and mine opinions* o *Extract named entities* con una reseña del restaurante.
4. **Language Studio → Proyecto `hw8-restaurante-luis` → Schema definition / Data labeling**: vista de las 6 intenciones (`RealizarPedido`, `ConsultarMenu`, etc.) y las 5 entidades (`Plato`, `Cantidad`, etc.).
5. **Model performance**: métricas de evaluación del modelo `v1` (macro/micro F1 e intenciones).
6. **Deploying a model**: despliegue `production` apuntando al modelo `v1`.
7. **Testing deployments**: probar las frases `"Quiero pedir una pizza"` y `"¿Cuál es el menú de hoy?"` mostrando intención principal, confianza y entidades detectadas.
8. **Exportar proyecto**: botón **Export** en Language Studio o vista del archivo local `infra/nlp/out/hw8-restaurante-luis-export.json`.

## 6. Dificultades encontradas

1. **Retiro de LUIS clásico:** `LUIS` y `LUIS.Authoring` no tienen SKUs disponibles en las regiones permitidas; se resolvió usando **CLU** en Azure AI Language (`TextAnalytics`, F0), que es su reemplazo oficial.
2. **Esquema de entrenamiento CLU `2023-04-01`:** el parámetro correcto es `modelLabel` (en lugar de `trainedModelLabel`) y `trainingSplitPercentage`/`testingSplitPercentage` dentro de `evaluationOptions`.
3. **Idioma español (`es`):** `trainingMode: "standard"` devuelve `Training config not support for project kind: Conversation`; para proyectos en español se requiere `trainingMode: "advanced"` (modelo transformer multilingüe).
