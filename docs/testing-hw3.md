# Pruebas HW3

Base ALB: `http://cloudtask-alb-1207092219.us-east-1.elb.amazonaws.com` (`/` → web, `/api/*` → API).

## 1. Funcionalidad a través del ALB
| # | Operación | Resultado |
|---|---|---|
| 1 | `GET /` | `200` (web Next.js) |
| 2 | `GET /api/` | `Hello World!` (API) |
| 3 | `GET /api/tasks` | `200 []` (RDS conectada, esquema aplicado solo) |
| 4 | `POST /api/tasks/upload` + `POST /api/tasks` con `imgUrl` | `200` + URL S3; tarea `id:1` persistida |
| 5 | `GET /api/tasks` | tarea con `imgUrl` de S3 |

## 2. Alta disponibilidad
- 4/4 destinos `healthy` (2 instancias × 2 TGs) repartidos en `1a` y `1b`.
- Terminado manual de `i-0ae28dcf53278f942` → ASG lanzó `i-0180d48906f12810b`, **InService en ~2 min**,
con la app respondiendo `200` durante todo el evento.

## 3. Escalado automático (evento real)
Quema de CPU en ambas instancias vía SSM (13 min):
| Tiempo | `cloudtask-cpu-high` | Deseado/instancias |
|---|---|---|
| t+2…10 min | OK | 2 / 2 |
| **t+12 min** | **ALARM** | **3 / 3** (`Launching a new EC2 instance … Successful`) |

Evidencia: actividad del ASG + alarma en ALARM + 3 destinos healthy. (El burn terminó a los 13 min;
el scale-in (< 30 %) actuaría después con su cooldown.)

## 4. Carga (referencia HW2, monoinstancia)
`GET /api/tasks`: 87 req/s, 0 fallos; `POST`: 40 req/s, 200/200 persistidos; web: 41,6 req/s, 0 fallos.
Con 2+ instancias tras el ALB la capacidad se multiplica; el cuello de botella pasa a ser RDS Single-AZ
(aceptado para el curso; producción: Multi-AZ + réplicas de lectura).
