# Implementación HW4 paso a paso (CloudFormation + CLI, us-east-1)

Plantilla: `infra/cloudformation.yaml`. Validada con `cfn-lint` (solo queda el aviso informativo W1011:
el password de RDS se pasa por parámetro NoEcho en vez de Secrets Manager — aceptado para el curso).

## 1. Despliegue automatizado (un comando)

```bash
DBPASS=$(cat ~/.config/cloudtask/rds-password)
aws cloudformation deploy --template-file infra/cloudformation.yaml \
  --stack-name cloudtask-hw4 \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --parameter-overrides DBPassword="$DBPASS" \
  --tags Project=cloudtask-hw4 --region us-east-1
```

Esto crea VPC, subredes, IGW, NAT, rutas, NACLs, SGs, S3, ECR, IAM, RDS (~15 min),
ALB + reglas, cluster ECS, launch template, ASG, capacity provider, task definitions,
servicios, auto scaling y alarmas. Salidas: `AlbDNS`, `WebURL`, `ApiURL`, `RdsEndpoint`, `BucketName`.

## 2. Imágenes de contenedores

La API se reutiliza sin recompilar (imagen local verificada en HW2/HW3):

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com
docker push <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-api:latest
```

La web se reconstruye **después** de conocer el DNS del ALB (`NEXT_PUBLIC_API_URL` se incrusta al compilar):

```bash
ALB=$(aws cloudformation describe-stacks --stack-name cloudtask-hw4 \
  --query 'Stacks[0].Outputs[?OutputKey==`AlbDNS`].OutputValue' --output text --region us-east-1)
docker build -f apps/web/Dockerfile --build-arg NEXT_PUBLIC_API_URL=http://$ALB/api \
  -t <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-web:latest .
docker push <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-web:latest
# si el servicio web arrancó antes del push:
aws ecs update-service --cluster cloudtask-cluster --service cloudtask-web \
  --force-new-deployment --region us-east-1
```

## 3. Gestión con Systems Manager (sin SSH)

```bash
aws ssm send-command --instance-ids <ID1> <ID2> \
  --document-name AWS-RunShellScript --parameters '{"commands":["echo ssm-ok $(hostname)"]}' \
  --region us-east-1
# interactivo: aws ssm start-session --target <ID> --region us-east-1
```

Verificado: `Success` en ambas instancias (sin puerto 22 abierto en ningún SG).

## 4. Modelo de responsabilidad compartida

- **AWS:** seguridad física, red troncal, hipervisor, AMIs ECS-optimizadas base, hardware de
  ALB/RDS/NAT, plano de control de ECS/RDS/CloudFormation.
- **Estudiante:** plantilla y parámetros, SGs/NACLs/routeo, IAM y políticas, secretos
  (`DBPassword` por parámetro NoEcho; en producción: Secrets Manager), imágenes y dependencias,
  esquema (`prisma db push` al arrancar el contenedor), retención (sin snapshots por despliegue
  efímero), TLS hacia RDS (`?sslmode=require`), datos y accesos.

## 5. Dificultades

1. **Propiedad inválida `ScalingResourceId`** en la política de escalado (lo correcto es `ScalingTargetId`)
   + `HealthCheckPort: traffic-port` faltante con puertos dinámicos → detectado con `cfn-lint`, no a ciegas.
2. **Target group huérfano** (`cloudtask-api-tg` del redeploy de HW3, cuyo borrado nunca corrió) bloqueó el
   primer despliegue por nombre duplicado → se eliminó y se redesplegó.
3. **La web debe compilarse tras el ALB** (URL embebida) y el servicio puede arrancar antes del push →
   `force-new-deployment` lo resuelve; los servicios reintentan el pull solos.
4. **Teardown de CloudFormation:** el bucket S3 debe vaciarse antes de borrar el stack (los objetos bloquean
   el borrado); RDS lleva `DeletionPolicy: Delete` (sin snapshot final).

## 6. Capturas requeridas (consola AWS)

1. CloudFormation → stack `cloudtask-hw4` en `CREATE_COMPLETE` + pestaña Recursos/Salidas.
2. VPC → mapa de recursos (VPC, 6 subredes, IGW, NAT, tablas) + NACLs por tier.
3. EC2 → ALB con listeners/reglas (`/api/*`) + target groups con destinos `healthy` en 2 AZs.
4. ECS → clúster `cloudtask-cluster`, servicios `cloudtask-api/web` 2/2 + capacity provider + tareas.
5. Auto Scaling → ASG 2/2/4 + escalado del servicio (target tracking 70 %).
6. CloudWatch → 3 alarmas + Log groups `/ecs/cloudtask-*` con logs de contenedores.
7. RDS `Available` (privada, cifrada), S3 (objeto + URL), IAM (3 roles), SSM (comando `Success`).
8. Navegador → web vía DNS del ALB con la tarea demo (imagen S3).
