# Costos HW8 — Azure AI Language (South Central US)

| Recurso | Nivel | Consumo realizado | Costo |
|---|---|---|---|
| Azure AI Language (`lang-hw8-4632`) | **F0 (Free)** | 6 docs Text Analytics (~18 transacciones) + 1 proyecto CLU (64 frases, 1 entrenamiento, 18 predicciones, 1 exportación) | **$0.00** |
| Grupo de recursos (`rg-cloudtask-hw8`) | — | Contenedor lógico | **$0.00** |
| **Total** | | | **$0.00** |

## Límites del nivel F0 (referencia)

- 1 recurso F0 de Azure AI Language por suscripción.
- Text Analytics: hasta 5.000 registros de texto al mes.
- CLU: hasta 5.000 llamadas de predicción al mes y 1 hora de entrenamiento mensual.
- Para este laboratorio académico el consumo real quedó muy por debajo del tope gratuito, generando **$0.00** de cargo.

## Referencia en nivel S (Standard) si pasara a producción

- Text Analytics (Sentimiento / NER / Key Phrases): ~$2 por 1.000 registros de texto (primeros 500k).
- CLU entrenamiento `advanced`: cobro por hora de cómputo de entrenamiento (~$3/hora).
- CLU predicción runtime: ~$1 a $2 por 1.000 registros analizados.

## Limpieza (después de tomar las capturas en el portal)

```bash
az group delete --name rg-cloudtask-hw8 --yes --no-wait
```

El archivo exportado `infra/nlp/out/hw8-restaurante-luis-export.json` y los resultados JSON quedan guardados localmente en el repositorio sin generar costos.
