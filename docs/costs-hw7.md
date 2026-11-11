# Costos HW7 — Custom Vision (South Central US)

| Recurso | Nivel | Consumo | Costo |
|---|---|---|---|
| Custom Vision Training | **F0 (free)** | 1 proyecto, 60 imágenes, 1 entrenamiento rápido | **$0.00** |
| Custom Vision Prediction | **F0 (free)** | 20 predicciones de prueba | **$0.00** |
| Almacenamiento de imágenes | Incluido en el servicio | 80 imágenes (~10 MB) | **$0.00** |
| Exportación ONNX | Incluida | 1 descarga | **$0.00** |
| **Total** | | | **$0.00** |

## Límites del nivel F0 (referencia)

- 2 proyectos por recurso de entrenamiento.
- 5.000 imágenes de entrenamiento por proyecto; 50 etiquetas.
- 1 hora de entrenamiento al mes (el entrenamiento rápido usado toma segundos/minutos).
- 15.000 predicciones al mes por recurso de predicción.

## Si se usara el nivel S0 (producción)

- Entrenamiento: ~$20 por hora de cómputo.
- Predicción: ~$2 por 1.000 transacciones.
- Para este trabajo (1 entrenamiento corto + 20 predicciones) el costo sería de centavos,
  pero F0 ya cubre todo.

## Limpieza

```bash
az group delete --name rg-cloudtask-hw7 --yes --no-wait
```

Los modelos exportados quedan descargados localmente; no generan cargos.
