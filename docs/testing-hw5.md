# Pruebas y resultados HW5 — AutoML (regresión de precios)

Workspace `azureml-hw5` · Job `serene_head_1hrtd6fdbz` · Modelo registrado `automobile-price-best` v1.

## 1. Configuración del experimento

| Parámetro | Valor |
|---|---|
| Tarea | Regresión |
| Variable objetivo | `price` |
| Métrica primaria | `r2_score` |
| Dataset | UCI Automobile (imports-85), 201 filas, 25 features |
| Validación | Validación cruzada de 5 folds |
| Trials | 10 (con early termination) |
| Tiempo límite | 20 min (job real ≈ 18 min, incluido arranque del clúster) |
| Featurización | Automática (imputación, one-hot, escalado) |
| Explicabilidad | Habilitada |

## 2. Métricas del mejor modelo

| Métrica | Valor | Lectura |
|---|---|---|
| **R²** | **0,8939** | Explica ~89,4 % de la varianza del precio |
| **RMSE** | **1950,35 USD** | Error cuadrático medio en unidades de precio |
| **MAE** | **1419,42 USD** | Error absoluto medio |
| MAPE | 10,65 % | Error porcentual medio |
| Varianza explicada | 0,9090 | Consistente con R² |
| Correlación de Spearman | 0,9448 | Buen ordenamiento relativo de precios |
| Error absoluto mediano | 1073,19 USD | La mitad de los errores está por debajo de este valor |

## 3. Modelos evaluados (10 trials)

Secuencia registrada por AutoML: LightGBM, XGBoostRegressor, XGBoostRegressor, ElasticNet,
LightGBM, XGBoostRegressor, RandomForest, RandomForest, StackEnsemble y **VotingEnsemble**.
El ganador fue el **VotingEnsemble** (combinación ponderada de los mejores modelos), con R² 0,8939.

## 4. Interpretación

- El precio de un automóvil se predice con un error medio de ~USD 1.4k, razonable para un rango de
  precios de USD 5k–45k y solo 201 ejemplos.
- Las variables con mayor peso esperado son `curb_weight`, `engine_size`, `horsepower`, `make` y
  `wheel_base`; al estar `make` en el dataset, existe riesgo de sesgo por marca que debe documentarse.
- La validación cruzada de 5 folds y el ensamble reducen el sobreajuste; aun así, el tamaño muestral
  limita la generalización a autos actuales.
- El job y el modelo quedan versionados en el workspace: trazabilidad completa (parámetros, datos,
  métricas y artefactos).

## 5. Evidencia generada

- Job completado: `serene_head_1hrtd6fdbz` (Estado **Completed**).
- Mejor corrida hija: `serene_head_1hrtd6fdbz_8` (VotingEnsemble).
- Modelo registrado: `automobile-price-best` versión 1 (custom model, `model.pkl`) con tags
  `r2=0.8939`, `rmse=1950.35`, `mae=1419.42`, `algorithm=VotingEnsemble`.
- Modelos auto-registrados por MLflow para cada trial (prefijo `azureml_serene_…`).
- Artefactos descargables: `model.pkl`, `scoring_file_v_2_0_0.py`, `featurization_summary.json`,
  `predicted_true`, `residuals`.

## 6. Cómo ver estos resultados en Azure ML Studio

1. **Jobs** → experimento `hw5-automobile-price` → `serene_head_1hrtd6fdbz`.
2. En **Details/Overview** se muestra **"Best model summary"** (VotingEnsemble) y el estado Completed.
3. Pestaña **"Models + child jobs"** (UI nueva: **"Models"**) → clic en **VotingEnsemble** → pestaña **"Metrics"**.
   Allí se marcan R², RMSE, MAE y se ven los gráficos (predicho vs. real, residuales).
4. **Models** → `automobile-price-best` → **Tags**: `r2`, `rmse`, `mae`, `algorithm`.
5. *(Opcional)* pestaña **Explanations** del job para importancia de variables.

> Nota: los nombres exactos de pestañas varían entre la UI clásica y la nueva; si no aparece "Metrics",
> usar la vista del modelo registrado (Tags) como evidencia alternativa.
