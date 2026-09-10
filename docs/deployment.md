# Implementación paso a paso — CloudTask en AWS

Región: `us-east-1`. Todo ejecutado con AWS CLI v2 desde Linux (perfil `cloudtask-deployer`).

## 0. Prerrequisitos

```bash
# AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
unzip -q /tmp/awscliv2.zip -d /tmp && sudo /tmp/aws/install
aws configure          # Access Key + Secret + region us-east-1 + json
aws sts get-caller-identity   # verificar
```

## 1. Bucket S3 para imágenes

El nombre `taskcloud2` (del código original) ya estaba ocupado globalmente (403 en `head-bucket`), así que se creó uno propio con lectura pública solo en `tasks/*`:

```bash
BUCKET="cloudtask-images-340514595007"
aws s3api create-bucket --bucket $BUCKET --region us-east-1
aws s3api put-public-access-block --bucket $BUCKET \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false
aws s3api put-bucket-policy --bucket $BUCKET --policy \
  '{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadTaskImages","Effect":"Allow",
    "Principal":"*","Action":"s3:GetObject",
    "Resource":"arn:aws:s3:::'$BUCKET'/tasks/*"}]}'
aws s3api put-bucket-cors --bucket $BUCKET --cors-configuration \
  '{"CORSRules":[{"AllowedOrigins":["*"],"AllowedMethods":["GET","HEAD"],
    "AllowedHeaders":["*"],"MaxAgeSeconds":3600}]}'
```

## 2. Red y seguridad

```bash
VPC="vpc-0db0e2240a9e7138c"   # VPC por defecto
# SG de cómputo: 22 (solo mi IP), 3000 y 3001 (demo pública)
aws ec2 create-security-group --group-name cloudtask-ec2-sg --vpc-id $VPC ...
aws ec2 authorize-security-group-ingress --group-id $EC2_SG --protocol tcp --port 22 --cidr <MI_IP>/32
aws ec2 authorize-security-group-ingress --group-id $EC2_SG --protocol tcp --port 3000 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $EC2_SG --protocol tcp --port 3001 --cidr 0.0.0.0/0
# SG de datos: 5432 solo desde el SG de cómputo
aws ec2 authorize-security-group-ingress --group-id $RDS_SG --protocol tcp --port 5432 --source-group $EC2_SG
```

Rol IAM para EC2 (sin claves estáticas en el servidor):

```bash
aws iam create-role --role-name cloudtask-ec2-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow",
    "Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
aws iam put-role-policy --role-name cloudtask-ec2-role --policy-name cloudtask-s3-images \
  --policy-document '{... PutObject/GetObject/DeleteObject en tasks/* + ListBucket ...}'
aws iam attach-role-policy --role-name cloudtask-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly
aws iam create-instance-profile --instance-profile-name cloudtask-ec2-profile
aws iam add-role-to-instance-profile --instance-profile-name cloudtask-ec2-profile \
  --role-name cloudtask-ec2-role
```

## 3. Base de datos RDS

```bash
aws rds create-db-instance --db-instance-identifier cloudtask-db \
  --db-instance-class db.t3.micro --engine postgres --engine-version 17.11 \
  --allocated-storage 20 --storage-type gp2 --db-name cloudtask_db \
  --master-username cloudtask --master-user-password '<GENERADA>' \
  --vpc-security-group-ids $RDS_SG --no-multi-az --no-publicly-accessible \
  --backup-retention-period 0 --no-deletion-protection
# Endpoint resultante:
# cloudtask-db.cc5s2oq48v8f.us-east-1.rds.amazonaws.com:5432
```

El esquema se aplica solo al arrancar la API (`prisma db push` en el entrypoint del contenedor).

## 4. Contenerización y registro

Se agregaron `apps/api/Dockerfile`, `apps/web/Dockerfile`, `.dockerignore` y `apps/api/entrypoint.sh` (ver código fuente). Luego:

```bash
aws ecr create-repository --repository-name cloudtask-api
aws ecr create-repository --repository-name cloudtask-web
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com
docker build -f apps/api/Dockerfile -t <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-api:latest .
docker push <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-api:latest
docker build -f apps/web/Dockerfile \
  --build-arg NEXT_PUBLIC_API_URL=http://34.231.188.151:3001/api \
  -t <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-web:latest .
docker push <ACCOUNT>.dkr.ecr.us-east-1.amazonaws.com/cloudtask-web:latest
```

> `NEXT_PUBLIC_API_URL` se incrusta al compilar el frontend: por eso la IP elástica se reservó antes (`34.231.188.151`).

## 5. Instancia EC2 y despliegue

```bash
aws ec2 allocate-address --domain vpc   # -> 34.231.188.151
aws ec2 create-key-pair --key-name cloudtask-key --query KeyMaterial --output text > cloudtask-key.pem
aws ec2 run-instances --image-id ami-081b0a6eac00b4f53 --instance-type t3.small \
  --key-name cloudtask-key --security-group-ids $EC2_SG \
  --iam-instance-profile Name=cloudtask-ec2-profile \
  --user-data file://user-data.sh   # instala docker, login ECR, docker run api+web
aws ec2 associate-address --instance-id <IID> --allocation-id <EIP_ALLOC>
```

Variables del contenedor API (`/etc/cloudtask/api.env` en la instancia): `DATABASE_URL` (con `?sslmode=require`), `PORT=3001`, `FRONTEND_URL=http://34.231.188.151:3000`, `AWS_REGION`, `AWS_S3_BUCKET` y `NODE_TLS_REJECT_UNAUTHORIZED=0` (ver dificultades).

## 6. Verificación

Ver `docs/testing.md` (CRUD, S3, carga).

## Dificultades encontradas

1. **Bucket `taskcloud2` ocupado** → 403 en `head-bucket`; se creó `cloudtask-images-...` con el ID de cuenta para unicidad.
2. **`t3.micro` throttled** (créditos CPU a cero por un contenedor en crash-loop) y la cuenta **no permite modo unlimited** → se migró a `t3.small`.
3. **Crash-loop del contenedor API**: pnpm no expone el binario `prisma` en el `.bin` raíz (vive en `packages/db/node_modules/.bin`) y faltaba `apps/api/node_modules` en la imagen final.
4. **RDS exige TLS** (`no pg_hba.conf entry ... no encryption`): se agregó `?sslmode=require`; como el driver verificaba la cadena del certificado, se añadió `NODE_TLS_REJECT_UNAUTHORIZED=0` (aceptable en demo; en producción se empaquetaría el CA de RDS).
5. **Regresión por merge**: la rama del compañero revirtió el `NotFoundException` de `get-task` (GET devolvía 200 vacío) → se restauró y redesplegó.

## Capturas requeridas (tomar de la consola AWS)

1. EC2 → instancia `cloudtask-app` en `running` con la IP elástica.
2. RDS → `cloudtask-db` en `Available` (motor, clase, almacenamiento).
3. S3 → bucket con un objeto en `tasks/` y su URL pública abierta en el navegador.
4. EC2 → grupos `cloudtask-ec2-sg` (puertos) y `cloudtask-rds-sg` (5432 interno).
5. IAM → rol `cloudtask-ec2-role` con la política inline del bucket + ECR.
6. ECR → repositorios con imagen `:latest`.
7. Navegador → web con una tarea que muestre imagen de S3.
