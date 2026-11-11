# Pruebas y resultados HW7 — Custom Vision (cats vs dogs)

Proyecto `hw7-cats-vs-dogs` · Iteración `b6f2d2f5-25db-4348-996b-bca86125d1ba` (`hw7-iter1`)
Dominio **General (compact)** · Clasificación **Multiclase** · Entrenamiento rápido.

## 1. Dataset

| Split | Gatos | Perros | Total |
|---|---|---|---|
| Entrenamiento | 30 | 30 | 60 |
| Hold-out (nunca visto) | 10 | 10 | 20 |

Imágenes del dataset público Cats vs Dogs (Microsoft/Kaggle), validadas y redimensionadas por el
servicio. Se descartaron archivos corruptos con Pillow antes de subirlos.

## 2. Métricas internas de Custom Vision (validación)

| Etiqueta | Precision | Recall | Average Precision |
|---|---|---|---|
| cats | 1,000 | 0,8333 | 1,000 |
| dogs | 1,000 | 1,000 | 1,000 |
| **Global** | **1,000** | **0,9167** | **1,000** |

## 3. Evaluación hold-out (20 imágenes reservadas)

Predicción vía endpoint publicado (`Prediction-Key`), eligiendo la etiqueta de mayor probabilidad:

| Métrica | Valor |
|---|---|
| **Accuracy** | **17/20 = 85,0 %** |
| Precision cats | 1,000 |
| Recall cats | 0,700 |
| Precision dogs | 0,769 |
| Recall dogs | 1,000 |

**Matriz de confusión**

| Real \ Predicho | cats | dogs |
|---|---|---|
| cats | **7** | 3 |
| dogs | 0 | **10** |

Errores: 3 gatos clasificados como perros, con probabilidades 0,6445 · 0,6859 · 0,7958. Ningún perro
fue clasificado como gato.

## 4. Interpretación

- El modelo es conservador con los gatos: no produce falsos positivos de gato (precision 1,0), pero
  pierde 3 de 10 (recall 0,70). Los perros se detectan perfectamente en esta muestra.
- La precisión global de Custom Vision (1,0) no equivale a una exactitud perfecta: la métrica interna
  se calcula sobre su propio split de validación y con umbrales por etiqueta; el hold-out independiente
  (85 %) es una estimación más realista.
- Con 30 imágenes por clase, el modelo aprende bien patrones generales, pero la variabilidad es alta:
  un solo error mueve 5 puntos porcentuales en el hold-out. Las 3 confusiones corresponden a gatos con
  poses/fondos atípicos.
- El sesgo del dataset (fotos de internet, principalmente razas comunes, fondos variados) limita la
  generalización a fotos reales de otras condiciones de iluminación o razas.

## 5. Prueba manual (Quick Test)

En Custom Vision Studio se subió una imagen nueva del set de prueba (`cats_test_000.jpg`); el modelo
devuelve las probabilidades por etiqueta en la ventana **Quick Test**. Esta captura complementa las
métricas y demuestra el uso del endpoint publicado.

## 6. Exportación

| Plataforma | Estado | Archivo |
|---|---|---|
| ONNX | **Done** | `out/hw7-cats-vs-dogs-onnx.zip` (4,4 MB) |

El ZIP contiene el modelo y los archivos de inferencia para ejecutarlo localmente o en el borde.
También quedó publicada la iteración en el recurso de predicción (`hw7-iter1`), lista para consumir
por REST.
