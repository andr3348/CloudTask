# Respuestas a las preguntas de análisis — HW7

## 1. ¿Qué ventajas ofrece Azure Custom Vision frente a entrenar un modelo desde cero?

- **Sin código ni infraestructura de ML:** el servicio entrena sobre modelos preentrenados (transfer learning);
  no hay que diseñar redes, instalar frameworks ni administrar GPU.
- **Flujo guiado en el portal:** crear proyecto, subir imágenes, etiquetar, entrenar y probar en minutos.
- **Métricas integradas:** precisión, recall y average precision por etiqueta, con iteraciones versionadas.
- **Inferencia administrada:** al publicar la iteración se obtiene un endpoint REST con autenticación,
  escalado y SLA de Azure.
- **Exportación:** los dominios compactos permiten exportar a ONNX, TensorFlow o CoreML para ejecutar
  en el borde (móvil, IoT) sin depender del servicio.
- **Costo inicial cero:** el nivel F0 permite 2 proyectos, 5.000 imágenes y cuotas mensuales de
  entrenamiento/predicción sin costo, ideal para prototipos y trabajos académicos.

## 2. ¿Qué desafíos se pueden presentar al entrenar con pocas imágenes?

- **Sobreajuste:** el modelo memoriza el pequeño conjunto y falla con imágenes nuevas.
- **Sesgo por fondo/contexto:** si todas las fotos de gatos son de interior y las de perros de exterior,
  el modelo aprende el fondo en lugar del animal (atajos espurios).
- **Poca variedad:** no cubre cambios de iluminación, ángulo, raza, tamaño u oclusión.
- **Métricas inestables:** con 10–20 imágenes de prueba, un solo error cambia varios puntos porcentuales;
  la estimación tiene alta varianza.
- **Desbalance de clases:** una clase con más ejemplos domina las predicciones.
- **Etiquetado escaso o ambiguo:** errores humanos se amplifican con pocos datos.

## 3. ¿Cómo podrían mejorar la precisión del modelo?

1. **Más datos y más diversos** (ángulos, fondos, iluminación, razas), manteniendo clases balanceadas.
2. **Etiquetado consistente** y revisión de imágenes dudosas; eliminar ejemplos corruptos o ambiguos.
3. **Evitar fuga de contexto:** recortar el objeto o variar fondos para que el modelo aprenda el sujeto.
4. **Aumento de datos** (volteos, recortes, cambios de brillo) y, si aplica, imágenes sintéticas.
5. **Separar entrenamiento/validación** de forma estratificada y usar un conjunto de prueba reservado.
6. **Iterar:** usar la pestaña Predictions de Custom Vision para corregir errores y reentrenar
   (aprendizaje activo).
7. **Elegir bien el dominio:** General (compacto) para exportar; General estándar si se prioriza precisión.
8. **Ajustar el umbral de probabilidad** según el costo de falsos positivos/negativos del negocio.

## 4. ¿Qué aplicaciones prácticas podría tener en la industria local (Perú)?

- **Retail y consumo masivo:** reconocimiento de productos en góndolas para inventario y planogramas;
  control de stock con fotos desde el móvil.
- **Agroexportación:** clasificación de calidad/defectos en arándanos, uvas, paltas o café; detección
  temprana de plagas y enfermedades en hojas con imágenes de campo.
- **Minería e industria:** verificación de uso de EPP (casco, chaleco) mediante detección de objetos,
  inspección visual de equipos y mantenimiento predictivo asistido por imágenes.
- **Turismo:** identificación de monumentos, sitios arqueológicos o especies para apps de guía.
- **Gestión de residuos y reciclaje:** separación automática de plástico, vidrio y cartón en plantas
  de reciclaje o puntos ecológicos.
- **Transporte:** clasificación de tipo de vehículo (auto, moto, camión) para conteo y peajes.
- **Salud (con supervisión médica):** preclasificación de imágenes dermatológicas o radiografías como
  apoyo al triaje, nunca como diagnóstico autónomo.

En todos los casos se requiere gobernanza de datos, evaluación de sesgos (por ejemplo, variedades
agrícolas o regiones poco representadas), supervisión humana y monitoreo del modelo en producción.
