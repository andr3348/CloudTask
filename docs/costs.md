# Costos estimados — CloudTask en AWS (us-east-1)

Precios on-demand aproximados, 730 h/mes. Alcance: demo del curso, tráfico mínimo.

| Servicio | Recurso | Cálculo | USD/mes |
|---|---|---|---|
| EC2 | `t3.small` (Linux) | 730 h × ~$0,0208 | **~$15,20** |
| RDS | `db.t3.micro` PostgreSQL (Single-AZ) | 750 h free tier (12 meses) | **$0** |
| RDS storage | 20 GB gp2 | 20 GB free tier | **$0** |
| S3 | < 1 GB imágenes + ~miles de requests | $0,023/GB + $0,0004/1000 PUT | **~$0,05** |
| ECR | ~1 GB imágenes | 500 MB free + $0,10/GB | **~$0,05** |
| Elastic IP | 1 IP asociada a instancia en ejecución | — | **$0** |
| Transferencia | < 1 GB salida (capa gratuita 100 GB) | — | **$0** |
| **Total con free tier + créditos** | | | **≈ $0 de bolsillo** |

## Sin free tier (referencia, 2.º año)

| Servicio | USD/mes |
|---|---|
| EC2 `t3.small` | ~$15,20 |
| RDS `db.t3.micro` + 20 GB gp2 + backup | ~$13,00 + ~$2,30 |
| S3 + ECR + transferencia demo | ~$0,20 |
| **Total** | **≈ $30/mes** |

## Notas de optimización

- Apagar la instancia EC2 y detener RDS fuera del horario de demo reduce el costo a casi $0 (solo EBS/S3 residuales).
- `t3.micro` calificaría a free tier total, pero se quedó sin créditos de CPU en este proyecto; para producción mínima se recomienda `t3.small` o créditos ilimitados.
- La EIP no cuesta mientras esté asociada; liberarla al terminar evita cargos ($0,005/h ociosa).
