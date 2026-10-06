# Pruebas HW4

Base ALB: `http://cloudtask-alb-764823881.us-east-1.elb.amazonaws.com` (`/` → web, `/api/*` → API).

## 1. Infraestructura como código
| # | Verificación | Resultado |
|---|---|---|
| 1 | `cfn-lint infra/cloudformation.yaml` | 0 errores (solo aviso W1011 documentado) |
| 2 | Stack `cloudtask-hw4` | `CREATE_COMPLETE`, ~100 recursos, salidas correctas |

## 2. Conectividad y app (por el ALB)
| # | Operación | Resultado |
|---|---|---|
| 1 | `GET /` | `200` (Next.js desde ECS) |
| 2 | `GET /api/` | `Hello World!` (NestJS desde ECS) |
| 3 | `GET /api/tasks` | `200 []` (RDS conectada, esquema aplicado solo) |
| 4 | `POST /api/tasks/upload` + `POST /api/tasks` con `imgUrl` | `200` + URL S3; tarea `id:1` persistida |
| 5 | Navegador en la web | tarea demo con imagen S3 renderizada |

## 3. Alta disponibilidad y seguridad
- Servicios 2/2 tareas `healthy` en `1a` + `1b`; instancias sin IP pública; SG 22 inexistente.
- SSM Run Command en ambas instancias: `Success` (gestión sin SSH).

## 4. Monitoreo y escalado
- 3 alarmas creadas (`api-cpu-high` OK, `alb-5xx`/`unhealthy-hosts` OK); target tracking 70 % activo
  (servicio 2–6 tareas, capacity provider suma EC2 según demanda).
- Logs de ambos contenedores en CloudWatch Logs con retención de 7 días.

## 5. Carga (referencia HW2/HW3)
Monoinstancia: GET 87 req/s y POST 40 req/s sin errores. Con 2 tareas por servicio tras el ALB la
capacidad se duplica; el escalado automático absorbe picos (tareas 2→6, EC2 2→4).
