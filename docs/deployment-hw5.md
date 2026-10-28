# Implementación HW5 paso a paso (Azure CLI + Azure ML)

Región `eastus`, suscripción personal (Azure free, $200 de crédito).

## 0. Herramientas

```bash
# Azure CLI (instalación de usuario, sin sudo) + extensión ML
az version            # 2.91.0
az extension add -n ml
az login --use-device-code
az account show       # Azure subscription 1 (Enabled)
```

## 1. Grupo de recursos y workspace

```bash
az group create --name rg-cloudtask-hw5 --location eastus --tags project=cloudtask-hw5
az provider register --namespace Microsoft.MachineLearningServices --wait

az ml workspace create --name azureml-hw5 --resource-group rg-cloudtask-hw5 \
  --location eastus --display-name "CloudTask HW5" --tags project=cloudtask-hw5
```

El workspace crea automáticamente Storage Account, Key Vault, Application Insights y Log Analytics.

## 2. Compute target

```bash
az ml compute create --file infra/azureml/compute.yml \
  --resource-group rg-cloudtask-hw5 --workspace-name azureml-hw5
```

`cpu-cluster`: `Standard_DS3_v2` (4 vCPU / 14 GB), mínimo 0, máximo 2 nodos, idle 5 min
(escala a cero y no consume crédito entre ejecuciones).

## 3. Dataset

`infra/azureml/data/automobile_price.csv`: 201 filas, 25 variables + `price` (UCI Automobile).
Los `?` se convierten en vacío para que AutoML los impute; filas sin `price` se descartan.

```bash
az ml data create --name automobile-price --version 1 --type mltable \
  --path infra/azureml/data --resource-group rg-cloudtask-hw5 --workspace-name azureml-hw5 \
  --description "UCI Automobile price dataset (201 rows)"
```

## 4. Experimento AutoML (regresión)

Archivo `infra/azureml/automl-automobile.yml`:

```yaml
type: automl
experiment_name: hw5-automobile-price
compute: azureml:cpu-cluster
task: regression
primary_metric: r2_score
target_column_name: price
training_data:
  type: mltable
  path: azureml:automobile-price:1
n_cross_validations: 5
limits: { timeout_minutes: 20, max_trials: 10, max_concurrent_trials: 2,
          enable_early_termination: true }
featurization: { mode: auto }
training: { enable_model_explainability: true }
```

```bash
az ml job create --file infra/azureml/automl-automobile.yml \
  --resource-group rg-cloudtask-hw5 --workspace-name azureml-hw5
# job: serene_head_1hrtd6fdbz
```

## 5. Resultados y registro del modelo

El job terminó en estado **Completed** (~18 min incluyendo el arranque del clúster). Mejor corrida:
`serene_head_1hrtd6fdbz_8` (VotingEnsemble), con R² 0,8939 · RMSE 1950,35 · MAE 1419,42.

```bash
az ml job show -n serene_head_1hrtd6fdbz -g rg-cloudtask-hw5 -w azureml-hw5 \
  --query '{status:status, best:tags.automl_best_child_run_id}'

# descargar artefactos del mejor trial y registrar el modelo
az ml job download -n serene_head_1hrtd6fdbz_8 -g rg-cloudtask-hw5 -w azureml-hw5 \
  --download-path ./job8
az ml model create --name automobile-price-best --version 1 --type custom_model \
  --path ./job8/artifacts/outputs/model.pkl \
  --description "AutoML VotingEnsemble - UCI Automobile price regression (R2 0.894)" \
  -g rg-cloudtask-hw5 -w azureml-hw5

az ml model list -g rg-cloudtask-hw5 -w azureml-hw5 -o table
```

También quedaron auto-registrados los modelos MLflow de cada trial (`azureml_serene_…`).

## 6. Capturas requeridas

1. **Grupo de recursos** `rg-cloudtask-hw5` con todos los recursos (workspace, storage, key vault,
   app insights, log analytics).
2. **Workspace** `azureml-hw5` — vista general en Azure Portal.
3. **ML Studio → Compute** — `cpu-cluster` (tipo AmlCompute, DS3_v2, 0–2 nodos).
4. **ML Studio → Data** — `automobile-price` v1 con vista previa de la tabla.
5. **AutoML job** — configuración (regresión, `price`, 5-fold CV) o estado en ejecución.
6. **Job completado** — en la página del job, sección **Details/Overview** aparece **"Best model summary"**
   con el algoritmo ganador (VotingEnsemble) y su R². Para la tabla de métricas: pestaña
   **"Models + child jobs"** (en la UI nueva, **"Models"**) → clic en el algoritmo ganador → pestaña
   **"Metrics"** (marcar R², RMSE, MAE). Alternativa garantizada: **Models → automobile-price-best →
   Tags**, donde se registraron `r2=0.8939`, `rmse=1950.35`, `mae=1419.42`.
7. **Modelo registrado** — `automobile-price-best` en Models (con las etiquetas de métricas).
8. (Opcional) Explicación del modelo / importancia de variables.

> Acceso: https://ml.azure.com → workspace `azureml-hw5`. El portal también enlaza a Studio
> desde la vista general del recurso ("Launch studio").

## 7. Costos

Ver `costs-hw5.md`: < $0.50 con el crédito de $200 (compute se apaga solo; workspace sin costo fijo).
Al finalizar: `az group delete --name rg-cloudtask-hw5 --yes --no-wait` borra todo el entorno.
