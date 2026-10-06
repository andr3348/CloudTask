# Implementación HW3 paso a paso (AWS CLI, us-east-1)

## 1. VPC y red
VPC `10.0.0.0/16` con hostnames DNS; 6 subredes (tabla en `architecture-hw3.md`); IGW; RT pública (`→ IGW`)
y privada (`→ NAT GW` en `public-1a`, EIP propia); 3 NACLs con reglas por capa y asociación a subredes.

## 2. Seguridad base
SGs `cloudtask-alb-sg` (80 mundo), `cloudtask-app-sg` (3000/3001 solo desde ALB-SG), `cloudtask-data-sg`
(5432 solo desde app-SG). Rol `cloudtask-ec2-role` + perfil `cloudtask-ec2-profile` (S3 acotado, ECR lectura, SSM).

## 3. Servicios compartidos
S3 (nombre reutilizado tras el teardown), ECR recreados + push de la imagen API local; RDS `db.t3.micro`
PG 17 en grupo de subredes data (privada, sin snapshot al borrar).

## 4. Balanceo y cómputo
Target groups `:3000` (health `/`) y `:3001` (health `/api/`); ALB + listener 80 (defecto → web) +
regla prioridad 10 (`/api/*` → API). Con el DNS del ALB se reconstruyó la imagen web
(`NEXT_PUBLIC_API_URL=http://<ALB>/api`) y se publicó. Launch template AL2023 `t3.micro` sin IP pública;
ASG 2/2/4 en subredes app con ambos TGs y health-check ELB.

## 5. Monitoreo y escalado
Políticas `cpu-scale-out` (+1) / `cpu-scale-in` (−1) con cooldown 300 s; 4 alarmas CloudWatch (tabla en
`architecture-hw3.md`). Quema de CPU vía SSM (13 min, ambos núcleos) → alarma ALARM a los ~12 min y
deseado 2→3 con actividad `Successful` registrada. Terminado de una instancia → reemplazo InService en ~2 min.

## 6. Modelo de responsabilidad compartida
- **AWS (“de” la nube):** seguridad física, red troncal, hipervisor, hardware del ALB/RDS/NAT, parches del
plano de control de RDS.
- **Estudiante (“en” la nube):** AMIs y parches del SO huésped, SGs/NACLs/routeo, IAM y políticas, secretos
(`DATABASE_URL` solo en user-data/env root-only), código y dependencias (imágenes), copias/retención
(decisión: sin snapshots por ser efímero), cifrado en tránsito hacia RDS (`sslmode=require`), datos y accesos.

## 7. Dificultades
1. La imagen web debe compilarse **después** de conocer el DNS del ALB (variable pública embebida) → orden
ALB → build → ASG.
2. `prisma db push` corre en cada arranque; con 2+ arranques concurrentes hay carrera de DDL (idempotente,
sin efecto real; en producción usar migraciones versionadas con un job único).
3. Sin SSH en subredes privadas: todo el diagnóstico vía SSM (verificar agente + política antes de necesitarlo).

## 8. Capturas requeridas (consola AWS)
1. VPC → mapa de recursos (VPC, subredes, IGW, NAT, tablas).
2. EC2 → balanceadores: listeners y reglas (`/api/*`).
3. Target groups: 2–3 destinos `healthy` en 1a+1b.
4. Auto Scaling: grupo (2/2/4), políticas y **historial de actividad** con el scale-out.
5. CloudWatch: alarma `cloudtask-cpu-high` en ALARM + historial.
6. RDS, S3 (objeto + URL) e IAM (rol con sus 3 políticas).
7. Navegador: web vía DNS del ALB con tarea con imagen S3.
