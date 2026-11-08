
# Proyecto Final - Biblioteca GKE

## Universidad Rafael Landívar
Curso: Virtualización  
Proyecto Final - Segundo semestre 2026

## Descripción
Sistema web para la administración de una biblioteca,
desarrollado mediante una arquitectura de microservicios
y desplegado en Google Kubernetes Engine (GKE).

## Caso de uso
Caso 4: Biblioteca

Entidades principales:
- Ejemplares
- Préstamos

Cada entidad dispone de operaciones CRUD:
crear, consultar, actualizar y eliminar.

Los préstamos están relacionados con los ejemplares.

## Arquitectura

[Ver diagrama de arquitectura](docs/arquitectura/arquitectura.md)
El sistema está compuesto por:

- Frontend web
- Microservicio de Ejemplares
- Microservicio de Préstamos
- Base de datos persistente
- Kubernetes en Google Cloud
- Google Artifact Registry
- Terraform

## Integrantes
Pendiente de completar con nombres y carnés.

## Estructura del proyecto

- `main.tf`: infraestructura principal de Google Cloud.
- `variables.tf`: variables de configuración de Terraform.
- `outputs.tf`: valores de salida de Terraform.
- `terraform.tfvars.example`: ejemplo de variables para el despliegue.
- `frontend/`: interfaz web de la biblioteca (pendiente de integración).
- `microservicios/ejemplares/`: API CRUD de ejemplares (pendiente).
- `microservicios/prestamos/`: API CRUD de préstamos (pendiente).
- `k8s/`: manifiestos Kubernetes (pendiente).
- `docs/arquitectura/`: documentación y diagrama de arquitectura.
- `docs/costos/`: estimaciones de costos de Google Cloud.
- `docs/evidencias/`: evidencias del proyecto final.

## Configuración de infraestructura

- **Equipo:** Holdovers
- **Clúster:** `holdovers-gke`
- **Región:** `us-central1`
- **Zona:** `us-central1-a`
- **Namespace:** `holdovers`
- **Node pool:** `pool-holdovers`
- **Nodos:** 2 máquinas `e2-small` Spot
- **Artifact Registry:** `holdovers`
- **Cuenta de servicio de nodos:** `nodos-holdovers`

La infraestructura se administra mediante Terraform. Los recursos de Kubernetes se desplegarán utilizando manifiestos YAML.

## Imágenes Docker

Las imágenes previstas para el sistema son:

- `frontend:v1`
- `ejemplares:v1`
- `prestamos:v1`

El prefijo de Artifact Registry se obtiene mediante:

`terraform output -raw ruta_imagenes`

La construcción y publicación de las imágenes se realizará cuando los componentes estén disponibles y el repositorio de Artifact Registry haya sido creado.

## Despliegue
Pendiente de completar cuando se integre
la infraestructura y los microservicios.

## Evidencias
Las evidencias del proyecto estarán organizadas
según las secciones A-G de la rúbrica.
