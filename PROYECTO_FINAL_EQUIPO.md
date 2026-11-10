# Proyecto Final GKE: Biblioteca (equipo holdovers)

Documento único del equipo. Incluye el contrato entre piezas y las instrucciones de cada integrante.

## Índice

1. Contrato de interfaces
2. Daniel: Infraestructura
3. José Carlos: Kubernetes
4. Alejandro: Microservicio A (Ejemplares)
5. Débora: Microservicio B (Préstamos)
6. Jhonatan: Frontend y base de datos
7. José Rodrigo: Imágenes, documentación y evidencias


---

# Contrato de interfaces: Biblioteca (Proyecto Final GKE, equipo holdovers)

Este documento define cómo se comunican las piezas. Cada integrante escribe su propio código siguiendo este contrato. No copiar código de otros equipos ni de proyectos anteriores.

## 1. Piezas y nombres

| Pieza | Imagen (sufijo) | Service de Kubernetes | Puerto interno | Responsable |
|---|---|---|---|---|
| Frontend (nginx + HTML) | `frontend:v1` | `frontend-svc` (tipo LoadBalancer, puerto 80) | 80 | Jhonatan Velasquez Fuentes |
| Microservicio A: Ejemplares | `ejemplares:v1` | `ejemplares-svc` (ClusterIP) | 8000 | Alejandro (integrante 3) |
| Microservicio B: Préstamos | `prestamos:v1` | `prestamos-svc` (ClusterIP) | 8000 | Débora (integrante 4) |
| Base de datos PostgreSQL 16 | `postgres:16` (espejo en Artifact Registry) | `postgres` (ClusterIP) | 5432 | Jhonatan Velasquez Fuentes |

Ruta completa de las imágenes: `<ruta_imagenes>/<imagen>`, por ejemplo `us-central1-docker.pkg.dev/<PROYECTO>/holdovers/ejemplares:v1`. El valor de `<ruta_imagenes>` sale del output `ruta_imagenes` de Terraform.

Namespace del equipo: `holdovers`. Clúster: `holdovers-gke`.

## 2. Base de datos

Una sola base llamada `biblioteca`, con tres tablas. Cada microservicio solo escribe en su tabla.

```sql
CREATE TABLE integrantes (
    carne   VARCHAR(10) PRIMARY KEY,
    nombre  VARCHAR(120) NOT NULL
);

CREATE TABLE ejemplares (
    id      SERIAL PRIMARY KEY,
    titulo  VARCHAR(200) NOT NULL,
    autor   VARCHAR(120) NOT NULL,
    anio    INTEGER
);

CREATE TABLE prestamos (
    id               SERIAL PRIMARY KEY,
    ejemplar_id      INTEGER NOT NULL REFERENCES ejemplares(id) ON DELETE RESTRICT,
    prestatario      VARCHAR(120) NOT NULL,
    fecha_prestamo   DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_devolucion DATE
);

INSERT INTO integrantes (carne, nombre) VALUES
('1187420', 'Alejandro René Gil Coto'),
('1315918', 'José Carlos Avalos Pérez'),
('1186023', 'Débora Eunice Hernández Gómez'),
('1247723', 'Juan Luis Daniel Ruano Lam'),
('1149123', 'Jose Rodrigo Valle Riveiro'),
('1137521', 'Jhonatan Velasquez Fuentes');
```

Las tablas se crean al primer arranque de PostgreSQL desde un ConfigMap montado en `/docker-entrypoint-initdb.d/`. Este script solo corre cuando el volumen está vacío.

Conexión desde los microservicios (variables de entorno):

- `DB_HOST=postgres`
- `DB_PORT=5432`
- `DB_NAME=biblioteca`
- `DB_USER` y `DB_PASSWORD` desde el Secret `db-credenciales`

## 3. Modelos JSON

**Ejemplar**

```json
{ "id": 1, "titulo": "Cien años de soledad", "autor": "Gabriel García Márquez", "anio": 1967 }
```

- `titulo` y `autor`: obligatorios, no vacíos.
- `anio`: opcional, entero.
- `id`: lo asigna el servidor, no se envía al crear.

**Préstamo**

```json
{ "id": 1, "ejemplar_id": 1, "prestatario": "Jhonatan Velasquez", "fecha_prestamo": "2026-11-09", "fecha_devolucion": null }
```

- `ejemplar_id`: obligatorio, debe existir en `ejemplares`.
- `prestatario`: obligatorio.
- `fecha_prestamo`: opcional al crear; si no se envía, se usa la fecha actual.
- `fecha_devolucion`: opcional, `null` mientras el libro no se devuelve.

**Integrante** (solo lectura)

```json
{ "carne": "1137521", "nombre": "Jhonatan Velasquez Fuentes" }
```

## 4. Endpoints de los microservicios

Ambos microservicios usan el mismo patrón.

| Método | Ruta | Respuesta exitosa | Errores |
|---|---|---|---|
| POST | `/api/ejemplares` | 201 + ejemplar | 400 si falta un campo |
| GET | `/api/ejemplares` | 200 + lista | |
| GET | `/api/ejemplares/{id}` | 200 + ejemplar | 404 |
| PUT | `/api/ejemplares/{id}` | 200 + ejemplar | 400, 404 |
| DELETE | `/api/ejemplares/{id}` | 204 | 404, 409 si tiene préstamos |
| GET | `/api/integrantes` | 200 + lista de integrantes | (solo en ejemplares) |
| GET | `/healthz` | 200 `{"status":"ok"}` | |

Igual para préstamos en `/api/prestamos`. En POST y PUT, si `ejemplar_id` no existe, responder 400.

Los errores siempre tienen la forma `{"error": "mensaje"}`.

**Decisión a aprobar:** el microservicio A expone `GET /api/integrantes`, porque el frontend no puede hablar con PostgreSQL directamente y el carné debe salir de la base de datos.

## 5. Enrutamiento del frontend (nginx)

El navegador no resuelve nombres DNS del clúster, así que nginx dentro del frontend actúa como proxy reverso:

```nginx
location /api/ejemplares/  { proxy_pass http://ejemplares-svc:8000; }
location /api/prestamos/   { proxy_pass http://prestamos-svc:8000; }
location /api/integrantes  { proxy_pass http://ejemplares-svc:8000; }
location /                 { root /usr/share/nginx/html; try_files $uri /index.html; }
```

El frontend solo llama rutas relativas (`/api/...`), nunca IPs ni nombres internos.

## 6. Requisitos de cada microservicio

- Python 3.12 con FastAPI y uvicorn (o el framework que prefieran, siempre que cumpla el contrato).
- Escucha en `0.0.0.0:8000`.
- Dockerfile propio en su carpeta.
- Lee la configuración solo de variables de entorno, sin credenciales escritas en el código.

## 7. Manifiestos Kubernetes (quién los escribe)

- Jhonatan (integrante 5): `postgres` (Deployment, Service, PVC de 1 GiB, ConfigMap con el SQL), `frontend` (Deployment, Service LoadBalancer; `nginx.conf` va dentro de la imagen).
- José (integrante 2, Kubernetes): namespace `holdovers`, Secret `db-credenciales`, ConfigMap `app-config` con `DB_HOST`, `DB_PORT`, `DB_NAME`, y los Deployments y Services de `ejemplares` y `prestamos`.
- Alejandro y Débora entregan sus Dockerfiles y código; José escribe sus manifiestos con las imágenes que ellos publiquen.
- Los Deployments de microservicios usan `imagePullPolicy: Always` y `replicas: 1` al inicio; luego se escalan a 3 para cumplir F1.

## 8. Decisiones confirmadas

1. Namespace y clúster: `holdovers` y `holdovers-gke`.
2. El microservicio A expone `GET /api/integrantes`.
3. Préstamos valida `ejemplar_id` consultando la tabla `ejemplares` directamente en la base, sin llamadas HTTP entre microservicios.
4. Asignación de integrantes: ver la carpeta `equipo/` con un archivo por persona.

---

# Daniel: Infraestructura (Terraform)

**Integrante:** Juan Luis Daniel Ruano Lam (1247723)
**Rol:** 1, Infraestructura (Terraform). Dificultad: alta.
**Referencias:** repo Biblioteca-GKE, CONTRATO_API.md, documento del proyecto (secciones 4, 5, 8 y anexo B).

## Qué debes hacer

- Mantener el repo Biblioteca-GKE: `main.tf`, `variables.tf`, `outputs.tf`, `.gitignore` y `terraform.tfvars.example`. El archivo `terraform.tfvars` nunca se sube a Git.
- Antes de crear nada, completar el pre-vuelo (sección 8): `gcloud auth list`, `gcloud config list`, facturación activa, APIs habilitadas, cuota de IPs y `terraform version`.
- Configurar una alerta de presupuesto en Google Cloud desde el primer día (sección 5).
- Ejecutar `terraform plan` y guardar su salida (D3), luego `terraform apply` y guardar su salida (D4).
- Verificar que el node pool queda con 2 nodos e2-small spot (D5).
- Preparar la estimación de costo mensual antes del despliegue (G1).
- Al terminar la defensa, ejecutar `terraform destroy` y guardar la salida (G2). La evidencia de destrucción vence el viernes 13 de noviembre a las 23:59.
- Cada captura debe mostrar el reloj del sistema y la salida de `gcloud config list` con el ID del proyecto. Sin eso el proyecto no se califica.

## Valores que deben quedar fijos

- Proyecto: el que ponga cada quien en `terraform.tfvars` (`project_id`).
- Región y zona: `us-central1` y `us-central1-a`.
- Clúster: `holdovers-gke`.
- Repositorio de Artifact Registry: `holdovers`.
- Namespace de Kubernetes: `holdovers`.

## Lo que afecta a otros integrantes

- **José Carlos (Kubernetes)** necesita el output `comando_credenciales` antes de empezar a desplegar.
- **Todos** necesitan el output `ruta_imagenes`. Formato: `us-central1-docker.pkg.dev/<PROYECTO>/holdovers/<imagen>:<tag>`.
- **José Rodrigo (imágenes)** necesita el ID del proyecto y el repositorio creado para hacer push.
- Si cambias región, zona, nombre del clúster o nombre del repositorio, avisa al equipo de inmediato. Todo el contrato depende de esos nombres.
- El node pool tiene solo 2 nodos e2-small. Todos los pods del proyecto deben caber ahí, así que avisa a José Carlos si ves que los pods se quedan en `Pending` por falta de recursos.
- Si aparece `ImagePullBackOff`, revisa primero la cuenta de servicio de los nodos: ya tiene permiso de lectura sobre el repositorio.

---

# José Carlos: Kubernetes

**Integrante:** José Carlos Avalos Pérez (1315918)
**Rol:** 2, Kubernetes. Dificultad: alta.
**Referencias:** CONTRATO_API.md (secciones 1, 2, 5 y 7), documento del proyecto (secciones 4 y 9, anexo B, sección E y F).

## Qué debes hacer

- Crear el namespace `holdovers` (`namespace.yaml`).
- Crear el Secret `db-credenciales` con las claves `DB_USER` y `DB_PASSWORD`. La contraseña nunca se escribe en el repo ni en el YAML que se suba a Git.
- Crear el ConfigMap `app-config` con `DB_HOST=postgres`, `DB_PORT=5432` y `DB_NAME=biblioteca`.
- Escribir los Deployments y Services de los microservicios:
  - `ejemplares` con Service `ejemplares-svc`, ClusterIP, puerto 8000.
  - `prestamos` con Service `prestamos-svc`, ClusterIP, puerto 8000.
  - Ambos reciben la configuración del ConfigMap y las credenciales del Secret como variables de entorno.
  - Las imágenes usan la ruta completa de `ruta_imagenes`, con tag `v1`.
- Arrancar con 1 réplica. Después escalar a 3 de forma declarativa (F1).
- Demostrar en vivo: eliminar un pod y ver que el Deployment lo recrea (F2), hacer rolling update cambiando el tag a `v2` (F3) y mostrar logs de un pod (F4).
- Evidencias: `kubectl get all -n holdovers` (E1), variable del ConfigMap dentro de un pod (E2), variable del Secret dentro de un pod (E3).
- Usar `imagePullPolicy: Always` en los Deployments de la aplicación.
- Definir `requests` y `limits` pequeños. Con e2-small la capacidad es baja.

## Lo que afecta a otros integrantes

- **Jhonatan** escribe el Deployment de PostgreSQL y el Deployment y Service LoadBalancer del frontend. Tú debes revisar esos archivos y aplicarlos después del Secret y el ConfigMap. Confirma con él el orden de aplicación.
- **Jhonatan** es quien verifica la IP pública del frontend, pero el criterio E5 lo cumple el equipo completo. Revisa que el `EXTERNAL-IP` se asigne (puede tardar 1 a 3 minutos).
- **Daniel** debe darte el comando de credenciales (`comando_credenciales`) y `ruta_imagenes` antes de empezar.
- **Alejandro** y **Débora** dependen de que `ejemplares-svc` y `prestamos-svc` tengan esos nombres exactos y el puerto 8000. Si cambias algo, avisa.
- Si un PVC queda en `Pending`, revisa `kubectl get storageclass`. Si el EXTERNAL-IP queda en `<pending>` persistentemente, revisa la cuota de IPs de la región.

---

# Alejandro: Microservicio A (Ejemplares)

**Integrante:** Alejandro René Gil Coto (1187420)
**Rol:** 3, Microservicio A: Ejemplares. Dificultad: media.
**Referencias:** CONTRATO_API.md (secciones 2, 3, 4 y 6), documento del proyecto (sección 4 y anexo B, criterios B1, B3, A4).

## Qué debes hacer

- Construir una API en Python 3.12 con FastAPI (o un framework equivalente que cumpla el contrato).
- Implementar los endpoints de la sección 4:
  - `POST`, `GET` (lista), `GET /{id}`, `PUT /{id}` y `DELETE /{id}` sobre `/api/ejemplares`.
  - `GET /api/integrantes`, de solo lectura, que devuelve la tabla `integrantes`.
  - `GET /healthz`, que responde `{"status":"ok"}`.
- Respetar la forma exacta del JSON de la sección 3:
  - Ejemplar: `id`, `titulo` (obligatorio), `autor` (obligatorio), `anio` (opcional).
  - Integrante: `carne`, `nombre`.
- Códigos de respuesta:
  - 201 al crear, 200 al consultar o actualizar, 204 al eliminar.
  - 400 si falta un campo obligatorio.
  - 404 si el ID no existe.
  - 409 si intentas eliminar un ejemplar que tiene préstamos. Esto lo detecta la llave foránea de la base; captura ese error y responde 409.
- Todos los errores tienen la forma `{"error": "mensaje"}`.
- Conectar a PostgreSQL usando las variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`. Ninguna credencial en el código.
- Escuchar en `0.0.0.0:8000`.
- Escribir tu propio Dockerfile en tu carpeta y publicar la imagen `ejemplares:v1` en la ruta de `ruta_imagenes`.
- Probar el CRUD completo en tu máquina antes de desplegar (B1).

## Lo que afecta a otros integrantes

- **Débora** consulta la tabla `ejemplares` para validar `ejemplar_id` en préstamos. No cambies los nombres de las columnas (`id`, `titulo`, `autor`, `anio`) sin avisar.
- Tú eres la única persona que escribe en la tabla `ejemplares`. Débora solo la lee, y nadie escribe en `integrantes` desde tu API.
- **José Carlos** crea el Deployment y el Service `ejemplares-svc` en el puerto 8000. Tu contenedor debe escuchar exactamente ahí.
- **Jhonatan** llama a `/api/ejemplares` y `/api/integrantes` desde el frontend. Mantén esas rutas exactamente como están en el contrato, porque el carné visible en pantalla (criterios A4 y B4) sale de `/api/integrantes`.
- Si necesitas cambiar un campo del JSON o una ruta, avisa al equipo antes de hacerlo.

---

# Débora: Microservicio B (Préstamos)

**Integrante:** Débora Eunice Hernández Gómez (1186023)
**Rol:** 4, Microservicio B: Préstamos. Dificultad: media.
**Referencias:** CONTRATO_API.md (secciones 2, 3, 4 y 6), documento del proyecto (sección 4 y anexo B, criterios B2, B3).

## Qué debes hacer

- Construir una API en Python 3.12 con FastAPI (o un framework equivalente que cumpla el contrato).
- Implementar los endpoints de la sección 4:
  - `POST`, `GET` (lista), `GET /{id}`, `PUT /{id}` y `DELETE /{id}` sobre `/api/prestamos`.
  - `GET /healthz`, que responde `{"status":"ok"}`.
- Respetar la forma exacta del JSON de la sección 3:
  - `id`, `ejemplar_id` (obligatorio y debe existir), `prestatario` (obligatorio), `fecha_prestamo` (opcional, por defecto la fecha actual), `fecha_devolucion` (opcional, `null` mientras no se devuelve).
- Validación del ejemplar: antes de crear o actualizar un préstamo, verifica con un `SELECT` en la tabla `ejemplares` de la misma base que `ejemplar_id` exista. Si no existe, responde 400 con `{"error": "..."}`.
- Esta validación se hace directamente en la base de datos. No llames por HTTP a `ejemplares-svc`; así no dependes de otro servicio para que funcione el tuyo.
- Códigos de respuesta: 201 al crear, 200 al consultar o actualizar, 204 al eliminar, 400 por datos inválidos y 404 si el préstamo no existe.
- Para registrar la devolución, usa `PUT /api/prestamos/{id}` y llena `fecha_devolucion`.
- Conectar a PostgreSQL con `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`. Ninguna credencial en el código.
- Escuchar en `0.0.0.0:8000`.
- Escribir tu propio Dockerfile y publicar la imagen `prestamos:v1` en la ruta de `ruta_imagenes`.

## Lo que afecta a otros integrantes

- **Alejandro** controla la tabla `ejemplares`. No escribas en ella.
- Tu tabla es `prestamos`. Nadie más escribe ahí.
- **José Carlos** crea el Deployment y el Service `prestamos-svc` en el puerto 8000.
- **Jhonatan** consume `/api/prestamos` desde el frontend. Si cambias un campo del JSON o una ruta, avisa al equipo antes.
- Si intentan eliminar un ejemplar con préstamos, la base responde con error de llave foránea. Eso lo maneja Alejandro en su API; tu API no debe permitir que un préstamo quede apuntando a un ejemplar inexistente.

---

# Jhonatan: Frontend y base de datos

**Integrante:** Jhonatan Velasquez Fuentes (1137521)
**Rol:** 5, Frontend y base de datos. Dificultad: media.
**Referencias:** CONTRATO_API.md (secciones 1, 2, 5 y 7), documento del proyecto (sección 4 y anexo B, criterios A4, B4, C1, E4, E5, E6).

## Qué debes hacer

### Base de datos
- Crear el Deployment de PostgreSQL 16 desde la imagen espejada en Artifact Registry (`<ruta_imagenes>/postgres:16`), con el Service `postgres` en el puerto 5432. Ver `mi-parte/k8s/bd/postgres.yaml`.
- Crear un PVC de 1 GiB y montarlo en `/var/lib/postgresql/data`. Usar `subPath` (por ejemplo `pgdata`) para evitar conflictos con el directorio de inicialización.
- Mapear las credenciales del Secret a las variables de la imagen oficial:
  - `POSTGRES_USER` desde `DB_USER`.
  - `POSTGRES_PASSWORD` desde `DB_PASSWORD`.
  - `POSTGRES_DB` desde `DB_NAME` (del ConfigMap).
- Crear un ConfigMap con el SQL inicial de la sección 2 del contrato (tablas `integrantes`, `ejemplares`, `prestamos` y los 6 carnés). Móntalo en `/docker-entrypoint-initdb.d/`.
- El SQL solo corre cuando el volumen está vacío. Para volver a sembrar datos hay que borrar el PVC.

### Frontend
- Crear una página HTML con JavaScript puro, sin dependencias externas, que:
  - Muestre la lista de integrantes (carné y nombre) desde `/api/integrantes`.
  - Muestre ejemplares desde `/api/ejemplares` y préstamos desde `/api/prestamos`.
  - Tenga formularios para crear, actualizar y eliminar en ambas entidades (criterio B4).
- Escribir `nginx.conf` con el proxy de la sección 5 del contrato. Va dentro de la imagen, así que no hace falta ConfigMap para él. El navegador solo llama rutas relativas `/api/...`.
- Escribir tu Dockerfile basado en `nginx:alpine` y publicar la imagen `frontend:v1` en la ruta de `ruta_imagenes`.
- Crear el Deployment del frontend y el Service `frontend-svc` de tipo LoadBalancer, puerto 80.

### Evidencias que te toca producir
- A4 y B4: captura del frontend mostrando los 6 carnés y datos de ambos microservicios.
- E4: crear un dato en la base, eliminar el pod de PostgreSQL, y mostrar que el dato sigue ahí.
- E5: captura de la IP pública abriendo el sitio desde un navegador externo.
- E6: demostrar que el frontend llega a los microservicios por nombre DNS.
- C1 para tu imagen: etiqueta con la ruta completa del repositorio.

## Lo que afecta a otros integrantes

- **José Carlos** debe aplicar el Secret `db-credenciales` y el ConfigMap `app-config` antes de que tus manifiestos de PostgreSQL y frontend funcionen. Coordina con él el orden de aplicación.
- **Alejandro** y **Débora** deben mantener exactamente las rutas `/api/ejemplares`, `/api/prestamos` e `/api/integrantes`. Si cambian algo, tu frontend se rompe.
- **Daniel** te da `ruta_imagenes` para publicar la imagen del frontend.
- **José Rodrigo** necesita tus capturas (A4, B4, E5, E6) para el PDF de evidencias.
- No modifiques las tablas desde el frontend. Todo cambio pasa por los microservicios.

---

# José Rodrigo: Imágenes, documentación y evidencias

**Integrante:** José Rodrigo Valle Riveiro (1149123)
**Rol:** 6, Imágenes, documentación y evidencias. Dificultad: media-baja.
**Referencias:** CONTRATO_API.md (secciones 1 y 8), documento del proyecto (secciones 7 y 9, anexo B, criterios A1 a A3, C1 a C3, G1 a G3).

## Qué debes hacer

### Imágenes (criterios C1 a C3)
- Construir las 3 imágenes que publica el equipo y etiquetarlas con la ruta completa de `ruta_imagenes`:
  - `ejemplares:v1`, `prestamos:v1` y `frontend:v1`.
- PostgreSQL también debe salir de Artifact Registry, porque C3 pide que los manifiestos referencien solo imágenes del repositorio. Espeja `postgres:16`: `docker pull postgres:16`, `docker tag postgres:16 <ruta_imagenes>/postgres:16` y `docker push <ruta_imagenes>/postgres:16`. Es una imagen adicional y no contradice C2.
- Hacer push al repositorio de Artifact Registry.
- Listar el repositorio para evidenciar que las imágenes existen (C2), por ejemplo con `gcloud artifacts docker images list`.
- Los manifiestos deben referenciar únicamente imágenes del repositorio (C3). Revisa que nadie use imágenes de Docker Hub.

### Documentación (criterios A1 a A3)
- README con:
  - El caso asignado: Caso 4, Biblioteca (Ejemplares y Préstamos).
  - Los 6 integrantes con su carné.
  - Instrucciones de despliegue.
- Diagrama de arquitectura propio que muestre frontend, microservicios, base de datos y el punto de entrada público (LoadBalancer).
- Control de commits: el repositorio debe tener al menos 10 commits distribuidos en 3 días distintos (A1). Coordina con todos para que cada integrante haga sus commits.

### Costos y evidencias (criterios G1 a G3)
- Estimación de costo mensual de la infraestructura, hecha antes del despliegue (G1).
- Captura del panel de facturación con el gasto final (G3).
- Armar el PDF de evidencias en el orden de las secciones A a G del anexo B. Cada captura debe mostrar el reloj del sistema y `gcloud config list`.

### Entrega
- Repositorio Git con código, Dockerfiles, `.tf`, manifiestos y README.
- PDF de evidencias.
- Subir todo al portal antes del martes 10 de noviembre a las 17:59.

## Lo que afecta a otros integrantes

- **Daniel** te da el ID del proyecto, el repositorio creado y `ruta_imagenes`. Necesitas eso para publicar las imágenes.
- **Alejandro**, **Débora**, **José Carlos** y **Jhonatan** deben entregarte sus capturas y sus archivos. Define una fecha límite interna, por ejemplo el lunes 9 de noviembre.
- Cada integrante construye su propia imagen desde su propio código. Tú haces el build y el push, pero no reescribes código de otros.
- Para el criterio G2, pide a Daniel la captura de `terraform destroy` después de la defensa.
