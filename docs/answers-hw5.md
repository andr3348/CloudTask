# Respuestas a las preguntas de análisis — HW5

## 1. ¿Qué ventajas ofrece AutoML frente a programar un modelo desde cero?

- **Velocidad:** automatiza limpieza/featurización (imputación, one-hot, escalado), selección de
  algoritmos y ajuste de hiperparámetros. Un experimento que a mano toma días se configura en minutos.
- **Cobertura de búsqueda:** prueba decenas de combinaciones (LightGBM, XGBoost, Random Forest,
  regresiones, ensambles) y aplica *early termination*, algo costoso de replicar manualmente.
- **Menos errores metodológicos:** validación cruzada y particiones consistentes, detección de
  problemas de datos (por ejemplo, fuga de información) y métricas reproducibles.
- **Explicabilidad y gobierno integrados:** importancia de variables, resúmenes de modelo y registro
  versionado de cada ejecución (trazabilidad).
- **Barrera de entrada baja:** perfiles de negocio/analistas pueden obtener un baseline sólido sin
  dominar Python ni MLOps; el científico de datos se concentra en el problema y los datos.
- **Integración con la nube:** el resultado queda registrado y listo para desplegar como endpoint,
  con monitoreo y control de acceso de Azure.

## 2. ¿Qué importancia tiene la IA responsable en modelos predictivos?

Un modelo puede ser técnicamente preciso y aun así causar daño. La IA responsable asegura:
**justicia** (no discriminar por marca, origen o género; auditar sesgos del dataset),
**confiabilidad y seguridad** (validar con datos no vistos, monitorear drift, evitar decisiones
irreversibles sin respaldo), **privacidad y seguridad** (minimizar datos personales, cifrado, control
de acceso), **transparencia** (explicar qué variables influyen y documentar el modelo),
**inclusividad** (funcionar para distintos segmentos) y **responsabilidad** (un humano revisa las
decisiones y existe trazabilidad). En un modelo de precios o de crédito, una predicción sesgada o no
explicable puede traducirse en pérdidas económicas o en trato injusto a personas, además de
incumplimientos regulatorios (por ejemplo, protección de datos personales).

## 3. ¿Qué limitaciones tiene el uso de modelos sin código frente al desarrollo personalizado?

- **Flexibilidad limitada:** AutoML cubre tareas tabulares, texto e imagen estándar; arquitecturas
  propias (redes específicas, series temporales complejas, multietiqueta) requieren código.
- **Menos control sobre el preprocesamiento:** transformaciones de negocio muy específicas, features
  derivadas o validaciones personalizadas no siempre se expresan en la interfaz.
- **Métricas y objetivos acotados:** si el negocio requiere una métrica compuesta o una función de
  pérdida particular, el catálogo puede no cubrirla.
- **Optimización de producción:** latencia, tamaño del modelo y costo de inferencia no se ajustan
  tan fino como con un modelo hecho a medida.
- **Dependencia del proveedor (lock-in):** el pipeline y el modelo viven en Azure; migrarlos exige
  rehacer trabajo.
- **Depuración y trazabilidad interna:** ante un comportamiento extraño, hay menos visibilidad del
  código que ejecuta el entrenamiento.
- **Costo/tiempo en problemas grandes:** barrer muchos trials puede ser más caro que una solución
  dirigida con conocimiento del dominio.

## 4. ¿Cómo se aplicaría en un caso práctico de la industria en Perú?

**Scoring de crédito para MYPES en una caja municipal o fintech.** Muchas MYPES no tienen historial
crediticio formal; una entidad podría usar AutoML para predecir probabilidad de incumplimiento a
partir de ventas declaradas, flujo transaccional, rubro, región y comportamiento de pagos, y así
ampliar el acceso al crédito con menor riesgo. El flujo sería: dataset tabular → AutoML (clasificación,
métrica AUC/recall) → explicabilidad por cliente → validación con el área de riesgos → endpoint por
lotes para evaluar solicitudes. Consideraciones locales: **calidad y representatividad de los datos**
(muchas MYPES informales), **sesgo geográfico/segmento** (no castigar zonas con menor historial),
**explicabilidad** para justificar rechazos, y cumplimiento de la **Ley 29733 de Protección de Datos
Personales** y de las normas de la SBS sobre riesgo crediticio. AutoML permite obtener un baseline
rápido y auditable; el juicio humano y la gobernanza siguen siendo imprescindibles.

Otros casos igualmente viables: predicción de precios agrícolas (papa, café) para cooperativas,
mantenimiento predictivo de equipos en minería, pronóstico de demanda para retail/turismo y
predicción de inasistencia a citas en clínicas.
