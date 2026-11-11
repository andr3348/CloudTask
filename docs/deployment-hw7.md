# Implementación HW7 paso a paso (Azure CLI + REST Custom Vision)

Suscripción **Azure for Students** (`1626065@senati.pe`) · Región **South Central US**.

## 0. Contexto y restricción regional

La suscripción tiene la política `sys.regionrestriction` (Allowed resource deployment regions):
`chilecentral`, `northcentralus`, `southcentralus`, `canadacentral`, `westus2`.
Custom Vision solo está disponible en `westus2`, `southcentralus` y `northcentralus`; se eligió
**South Central US** por cercanía a Perú. (Chile Central y Canadá Central no ofrecen Custom Vision.)

## 1. Herramientas y login

```bash
az login --use-device-code
az account set --subscription 463c2b2b-5d7e-4eb5-94d4-908a2e99053e
az provider register --namespace Microsoft.CognitiveServices --wait
```

## 2. Grupo de recursos y recursos Custom Vision (F0)

```bash
az group create --name rg-cloudtask-hw7 --location southcentralus --tags project=cloudtask-hw7

az cognitiveservices account create --name cv-hw7-train-4632 \
  --resource-group rg-cloudtask-hw7 --kind CustomVision.Training \
  --sku F0 --location southcentralus --yes --tags project=cloudtask-hw7

az cognitiveservices account create --name cv-hw7-pred-4632 \
  --resource-group rg-cloudtask-hw7 --kind CustomVision.Prediction \
  --sku F0 --location southcentralus --yes --tags project=cloudtask-hw7
```

Claves y endpoints:

```bash
az cognitiveservices account keys list -n cv-hw7-train-4632 -g rg-cloudtask-hw7 --query key1 -o tsv
az cognitiveservices account show -n cv-hw7-train-4632 -g rg-cloudtask-hw7 --query properties.endpoint -o tsv
```

## 3. Dataset

Se descargó el dataset público **Cats vs Dogs** (Microsoft/Kaggle, 12.501 imágenes por clase) y se
preparó un subconjunto validado con Pillow (`infra/customvision/prepare_dataset.py`):

- **Entrenamiento:** 30 gatos + 30 perros.
- **Prueba hold-out:** 10 gatos + 10 perros (nunca usados en entrenamiento).
- Se descartan imágenes corruptas o menores a 100 px.

```bash
uv run --with pillow python prepare_dataset.py \
  --src /tmp/opencode/cv/extracted/PetImages --out data
```

## 4. Proyecto y entrenamiento (REST v3.4-preview)

Custom Vision expone API de entrenamiento en `customvision/v3.4-preview/training` (minúsculas) con
el endpoint del recurso y cabecera `Training-Key`. El script `train_custom_vision.py` automatiza:

1. Selección del dominio **General (compact)** (exportable).
2. Creación del proyecto con `targetExportPlatforms=ONNX` (parámetros en query string).
3. Creación de etiquetas `cats` y `dogs`.
4. Carga por lotes (`POST /images/files`, JSON con contenido base64; hasta 64 imágenes por request).
5. Entrenamiento rápido: `POST /train?trainingType=Regular`.
6. Publicación: `POST /iterations/{id}/publish?publishName=hw7-iter1&predictionId=<ARM id del recurso Prediction>`.
7. Evaluación con las 20 imágenes hold-out.
8. Exportación `POST /iterations/{id}/export?platform=ONNX` y descarga del ZIP.

```bash
set -a; . ~/.config/cloudtask/cv.env; set +a
uv run --with requests python train_custom_vision.py --data data --out out
```

## 5. Resultados

- Iteración `b6f2d2f5-25db-4348-996b-bca86125d1ba`, publicada como `hw7-iter1`.
- Métricas de validación Custom Vision: **precision 1,0 · recall 0,9167 · AP 1,0**.
- Hold-out: **accuracy 85 % (17/20)**; ver `testing-hw7.md`.
- Export ONNX: `out/hw7-cats-vs-dogs-onnx.zip` (4,4 MB).

## 6. Capturas requeridas

1. **Grupo de recursos** `rg-cloudtask-hw7` con ambos recursos Custom Vision.
2. **Recurso de entrenamiento → Claves y punto de conexión** (ocultar/mosaicar las claves).
3. **customvision.ai → proyecto `hw7-cats-vs-dogs` → Settings**: dominio General (compact),
   tipo Classification / Multiclass, etiquetas.
4. **Training Images**: 30 imágenes `cats` + 30 `dogs` visibles con sus etiquetas.
5. **Performance**: pestaña de rendimiento con precision, recall, AP por etiqueta e iteración.
6. **Quick Test**: subir una imagen nueva (p. ej. `infra/customvision/data/test/cats/cats_test_000.jpg`)
   y capturar las probabilidades.
7. **Export**: iteración → Export → ONNX (y el ZIP descargado `out/hw7-cats-vs-dogs-onnx.zip`).
8. (Opcional) **Predictions**: imágenes de prueba clasificadas por el modelo.

> Portal: https://www.customvision.ai — iniciar sesión con `1626065@senati.pe` y elegir el
> directorio SENATI. El proyecto ya existe; no hay que crearlo de nuevo.

## 7. Dificultades encontradas

1. **Política regional de la suscripción estudiantil:** East US fue rechazado; se identificaron las
   regiones permitidas y se comprobó la disponibilidad de Custom Vision por región.
2. **Cambio de API:** la versión documentada `v3.4-preview` usa rutas en minúsculas, creación de
   proyecto con parámetros en query string y carga por lotes JSON base64 (`/images/files`), a diferencia
   de los ejemplos antiguos `v3.3/Training` con `POST /projects` y `/images/image` (devolvían 404).
3. **Publicación:** la API v3.4 exige `predictionId` (ID ARM del recurso Prediction); sin él devuelve 404.
4. **Exportación asíncrona:** la respuesta es una lista por plataforma y un segundo POST devuelve
   `BadRequestExportAlreadyInProgress`; hay que consultar el estado hasta `Done`.
5. **Paginación:** `GET /images` devuelve 50 por defecto; con `take=200` se confirman las 60 imágenes.
