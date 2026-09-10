# Pruebas — CloudTask en AWS

Base: `http://34.231.188.151:3001/api` · Web: `http://34.231.188.151:3000`

## 1. CRUD contra RDS (PostgreSQL)

| # | Operación | Resultado |
|---|---|---|
| 1 | `POST /tasks` `{"title":"DeployTest","status":"PENDING","priority":"HIGH"}` | `200` + objeto con `id:1`, defaults (`PENDING`/`MEDIUM`/`null`) ✓ |
| 2 | `GET /tasks/2` | `200` + objeto ✓ |
| 3 | `PUT /tasks/2` (cambio de estado, prioridad e `imgUrl`) | `200` + `updatedAt` actualizado ✓ |
| 4 | `GET /tasks` | `200` + lista (2 elementos) ✓ |
| 5 | `DELETE /tasks/2` | `200` cuerpo vacío ✓ |
| 6 | `GET /tasks/2` (eliminada) | `404` `{"message":"Task with id 2 not found"}` ✓ |
| 7 | `DELETE /tasks/99999` | `404` ✓ |
| 8 | `GET /tasks/abc` | `400` (ParseIntPipe) ✓ |
| 9 | `POST /tasks` con `status:"NOPE"` | `400` con mensaje de validación ✓ |

## 2. S3: carga y visualización

| # | Operación | Resultado |
|---|---|---|
| 1 | `POST /tasks/upload` (PNG, multipart `file`) | `200` `{"url":"https://cloudtask-images-340514595007.s3.us-east-1.amazonaws.com/tasks/..."}` ✓ |
| 2 | `GET` de la URL devuelta (navegador/curl) | imagen visible (objeto público) ✓ |
| 3 | `PUT /tasks/:id` con esa `imgUrl` + visualización en la tarjeta del frontend | imagen renderizada desde S3 ✓ |
| 4 | `PUT` con otra imagen / `DELETE` de la tarea | objeto anterior eliminado del bucket (sin huérfanos) ✓ |
| 5 | Subida de no-imagen / >10 MB | `400` ✓ |

## 3. Carga básica (`ab`, ApacheBench)

| Prueba | Carga | Rendimiento | Fallos |
|---|---|---|---|
| `GET /api/tasks` | 1000 req, conc. 20 | **87,0 req/s**, media 230 ms, p95 229 ms, p99 364 ms | 0 |
| `POST /api/tasks` | 200 req, conc. 10 | **40,1 req/s**, media 250 ms | 0 reales* |
| `GET /` (web Next.js) | 200 req, conc. 10 | **41,6 req/s**, media 240 ms, p95 323 ms | 0 |

\* `ab` reportó 194 "fallidos" en el POST, pero fue un artefacto de su comparación de longitud de respuesta (cada `201` trae id/timestamp únicos): se verificó que las **200 filas quedaron persistidas** en RDS y el log de la API mostró **0 errores**. Las 200 filas de prueba se eliminaron después vía `DELETE`, dejando la demo limpia.

**Conclusión de carga:** la instancia `t3.small` absorbe sin errores ~80 lecturas/s y ~40 escrituras/s con latencias p95 < 350 ms — de sobra para la demostración del curso.
