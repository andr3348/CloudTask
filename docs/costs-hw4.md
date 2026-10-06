# Costos HW4 (us-east-1, despliegue efímero de ~1 día / 8 h efectivas)

| Servicio | Recurso | Cálculo | USD |
|---|---|---|---|
| ALB + LCU | 8 h | 8 × ~$0,025 + LCUs demo | ~$0,25 |
| NAT GW | 8 h + poco tráfico | 8 × ~$0,045 | ~$0,40 |
| EC2 | 2 × `t3.micro` | horas free tier | $0 |
| RDS | `db.t3.micro` + 20 GB gp2 | free tier 12 meses | $0 |
| ECR/S3/logs/transferencia demo | mínimos | free tier | ~$0,10 |
| **Total jornada** | | | **≈ $1** |

## Encendido un mes (referencia)
ALB ~$18 + NAT GW ~$33 + EC2/RDS en free tier ≈ **$51/mes** (≈ $70 sin free tier).
Recomendaciones: NAT por AZ y Multi-AZ solo en producción; apagar/borrar el stack fuera de demo
(un `delete-stack` + vaciado previo del bucket deja la cuenta en $0).
