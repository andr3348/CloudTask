# Guía de Instalación y Configuración del Entorno (CloudTask)

Esta guía explica los pasos necesarios para que cualquier desarrollador configure y ejecute el proyecto CloudTask en local tras clonar el repositorio.

---

## 1. Variables de Entorno (.env)

El proyecto utiliza variables de entorno en 3 lugares clave. Para cada uno, se debe copiar el archivo `.env.example` correspondiente:

### A. Frontend Web (`apps/web`)
Crea el archivo `apps/web/.env.local`:
```bash
cp apps/web/.env.example apps/web/.env.local
```
**Contenido:**
```env
# URL de la API del Backend (NestJS)
NEXT_PUBLIC_API_URL="http://localhost:3001/api"
```

---

### B. Base de Datos / Prisma (`packages/db`)
Crea el archivo `packages/db/.env`:
```bash
cp packages/db/.env.example packages/db/.env
```
**Contenido:**
```env
# Cadena de conexión a PostgreSQL
DATABASE_URL="postgres://usuario:contraseña@localhost:5432/task_db"
```

---

### C. Backend API (`apps/api`)
Crea el archivo `apps/api/.env`:
```bash
cp apps/api/.env.example apps/api/.env
```
**Contenido:**
```env
# Cadena de conexión a PostgreSQL y puerto de ejecución
DATABASE_URL="postgres://usuario:contraseña@localhost:5432/task_db"
PORT=3001
FRONTEND_URL="http://localhost:3000"
```

---

## 2. Instalación de Dependencias

Desde la **raíz del proyecto**, instala las dependencias de todo el monorepo con `pnpm`:

```bash
pnpm install
```

---

## 3. Preparación de la Base de Datos

1. Navega al paquete de base de datos:
   ```bash
   cd packages/db
   ```
2. Sincroniza el esquema con PostgreSQL:
   ```bash
   pnpm run db:push
   ```
3. Compila el cliente y tipos de Prisma:
   ```bash
   pnpm run build
   ```

---

## 4. Ejecución del Proyecto

### Opción A: Ejecutar todo el Monorepo (Recomendado)
Desde la raíz del proyecto:
```bash
pnpm dev
```

### Opción B: Ejecutar por separado en terminales independientes

1. **Terminal 1 - Backend (NestJS):**
   ```bash
   cd apps/api
   pnpm run dev
   ```
   *Disponible en: `http://localhost:3001/api`*

2. **Terminal 2 - Frontend (Next.js):**
   ```bash
   cd apps/web
   pnpm run dev
   ```
   *Disponible en: `http://localhost:3000`*
