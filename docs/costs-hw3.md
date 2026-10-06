# Costos HW3 (us-east-1, despliegue efímero de ~1 día / 8 h efectivas)

| Servicio | Recurso | Cálculo | USD |
|---|---|---|---|
| ALB | 8 h + LCU mínimas | 8 × ~$0,025 + LCUs demo | ~$0,25 |
| NAT GW | 8 h + poco tráfico | 8 × ~$0,045 | ~$0,40 |
| EC2 | 2–3 × `t3.micro` | horas free tier (750 h/mes) | $0 |
| RDS | `db.t3.micro` + 20 GB | free tier 12 meses | $0 |
| S3/ECR/EIP-asociada/transferencia demo | mínimos | free tier | ~$0,05 |
| **Total jornada** | | | **≈ $1** |

## Si quedara encendido un mes (referencia)
ALB ~$18 + NAT GW ~$33 + EC2 micro (free) + RDS (free) ≈ **$51/mes**; sin free tier ≈ **$65/mes**.
Ahorros posibles: NAT por AZ solo en producción; apagar fuera de demo; `t3.micro` siempre que el CPU lo permita.
