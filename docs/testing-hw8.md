# Pruebas y resultados HW8 — Text Analytics y CLU (Restaurante)

Recurso: `lang-hw8-4632` (`TextAnalytics`, F0, `southcentralus`)  
Proyecto CLU: `hw8-restaurante-luis` · Modelo: `v1` (`advanced`, split 80/20) · Despliegue: `production`

## 1. Resultados de Text Analytics (`:analyze-text`)

### 1.1 Detección de idioma (6 muestras)

| ID | Extracto | Idioma detectado | Código ISO | Confianza |
|---|---|---|---|---|
| 1 | *"Excelente atención en el restaurante El Sabor Peruano..."* | Spanish | `es` | 1.00 |
| 2 | *"La pizza llegó fría después de una hora de espera..."* | Spanish | `es` | 1.00 |
| 3 | *"El menú ejecutivo tiene un precio razonable..."* | Spanish | `es` | 1.00 |
| 4 | *"El estudiante Diego Val de SENATI desarrolló..."* | Spanish | `es` | 1.00 |
| 5 | *"Great food and fast service! The pepperoni pizza..."* | English | `en` | 1.00 |
| 6 | *"A comida estava maravilhosa e o atendimento..."* | Portuguese | `pt` | 1.00 |

### 1.2 Sentimiento, entidades (NER) y palabras clave (muestras 1–4)

| ID | Sentimiento (pos / neu / neg) | Entidades detectadas (NER) | Palabras clave principales |
|---|---|---|---|
| 1 | **positive** (`0.99 / 0.01 / 0.00`) | `restaurante El Sabor Peruano` (Location), `Miraflores` (Location), `Lima` (Location), `lomo saltado` (Product), `chicha` (Product) | `Excelente atención`, `El Sabor Peruano`, `Miraflores`, `Lima`, `lomo`, `chicha` |
| 2 | **negative** (`0.00 / 0.03 / 0.97`) | `pizza` (Product), `una hora` (DateTime), `repartidor` (PersonType), `San Isidro` (Location), `delivery` (Skill) | `dirección`, `San Isidro`, `mala experiencia`, `pizza`, `espera`, `repartidor`, `delivery` |
| 3 | **positive** (`0.95 / 0.05 / 0.01`) | `menú ejecutivo` (Product), `un` (Quantity), `mozo` (PersonType) | `menú ejecutivo`, `atención`, `precio`, `porciones`, `mozo` |
| 4 | **neutral** (`0.00 / 1.00 / 0.00`) | `Diego Val` (Person), `SENATI` (Organization), `Microsoft Azure AI` (Product), `estudiante` (PersonType), `restaurante` (Location) | `Microsoft Azure AI Language`, `Diego Val`, `SENATI`, `asistente`, `pedidos`, `restaurante` |

Con *opinion mining* sobre el documento 1, el servicio asoció automáticamente los aspectos `atención` ← `Excelente`, `lomo saltado` ← `delicioso` y `chicha morada` ← `fresca` (100 % positivo).

## 2. Evaluación interna de CLU (split 80 % entrenamiento / 20 % prueba)

Sobre las 64 frases etiquetadas (6 intenciones, 5 entidades):

| Métrica | Intenciones | Entidades |
|---|---|---|
| **Micro Precision** | 0.9167 | 0.7778 |
| **Micro Recall** | 0.9167 | 0.7000 |
| **Micro F1** | **0.9167** | **0.7368** |
| **Macro F1** | 0.9111 | 0.8076 |

Detalle por intención: `RealizarPedido`, `ConsultarMenu`, `ReservarMesa` y `CancelarPedido` obtuvieron **F1 = 1.000**; `ConsultarHorarioUbicacion` obtuvo **F1 = 0.800** (P = 0.667, R = 1.000) y `None` obtuvo **F1 = 0.667** (P = 1.000, R = 0.500; 1 frase `None` de validación fue asignada a `ConsultarHorarioUbicacion`).

## 3. Evaluación hold-out independiente (18 frases nunca vistas)

- **Exactitud global de intenciones: 18/18 = 100.0 %**

| Frase de prueba | Intención real | Predicha (confianza) | Entidades extraídas | Respuesta simulada del sistema |
|---|---|---|---|---|
| *"Quiero pedir una pizza"* | `RealizarPedido` | `RealizarPedido` (**0.9999**) | `Cantidad="una"`, `Plato="pizza"` | ¡Pedido registrado! Prepararemos: pizza. |
| *"Tráeme dos platos de ceviche para llevar"* | `RealizarPedido` | `RealizarPedido` (**0.9999**) | `Cantidad="dos"`, `Plato="platos"`, `Plato="ceviche"`, `TipoServicio="para llevar"` | ¡Pedido registrado! Prepararemos: platos, ceviche (para llevar). |
| *"Quisiera ordenar un pollo a la brasa por delivery"* | `RealizarPedido` | `RealizarPedido` (**0.9999**) | `Cantidad="un"`, `Plato="pollo a la brasa"`, `TipoServicio="delivery"` | ¡Pedido registrado! Prepararemos: pollo a la brasa (delivery). |
| *"¿Cuál es el menú de hoy?"* | `ConsultarMenu` | `ConsultarMenu` (**0.9998**) | — | Menú de hoy: Lomo saltado (S/32), Ceviche mixto (S/35), Pizza familiar (S/45)... |
| *"Muéstrame los precios de las hamburguesas"* | `ConsultarMenu` | `ConsultarMenu` (**0.9978**) | `Plato="hamburguesas"` | Menú de hoy: Lomo saltado (S/32)... |
| *"Quiero reservar una mesa para 3 personas mañana a las 8 pm"* | `ReservarMesa` | `ReservarMesa` (**0.9999**) | `NumPersonas="3 personas"`, `FechaHora="mañana a las 8 pm"` | Mesa reservada para 3 personas (mañana a las 8 pm). ¡Te esperamos! |
| *"¿Cuál es la dirección del restaurante?"* | `ConsultarHorarioUbicacion` | `ConsultarHorarioUbicacion` (**0.9997**) | — | Atendemos de lunes a domingo de 12:00 p. m. a 11:00 p. m. en Av. Larco 450, Miraflores. |
| *"Por favor anulen mi orden de pizza"* | `CancelarPedido` | `CancelarPedido` (**0.9998**) | `Plato="pizza"` | Tu pedido ha sido cancelado sin costo. |
| *"¿Quién escribió Don Quijote de la Mancha?"* | `None` | `None` (**0.9992**) | `Plato="la Mancha"` *(falso positivo)* | No estoy seguro de entender tu solicitud... |

## 4. Interpretación y hallazgos

- El clasificador de intenciones logra **100 % en el hold-out** con confianzas > 0.997 en todas las intenciones de negocio (incluidos los ejemplos exactos de la guía: *"Quiero pedir una pizza"* y *"¿Cuál es el menú de hoy?"*).
- En la extracción de entidades aparecen dos mejoras claras para futuras iteraciones: (1) etiquetar `"platos"` fuera de `Plato` para no capturar unidades genéricas junto a `"ceviche"`, y (2) agregar frases `None` que incluyan nombres propios o lugares para evitar falsos positivos como `"la Mancha"` → `Plato`.

## 5. Modelo exportado

- Archivo: `infra/nlp/out/hw8-restaurante-luis-export.json` (21,370 bytes, versión de esquema `2023-04-01`, `Utf16CodeUnit`).
