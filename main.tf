# Proyecto Final - Virtualizacion
# Equipo: holdovers - Caso 4: Biblioteca
#
# Infraestructura como codigo: APIs, repositorio de imagenes (Artifact Registry),
# cluster GKE Standard zonal y node pool de 2 nodos e2-small spot.
# Los objetos de Kubernetes NO se gestionan aqui: se aplican con kubectl.

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zona
}

# ---------------------------------------------------------------------------
# APIs necesarias. disable_on_destroy = false evita que el destroy intente
# apagar las APIs del proyecto (lento y puede fallar).
# ---------------------------------------------------------------------------

locals {
  apis = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
  ])
}

resource "google_project_service" "apis" {
  for_each = local.apis

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# ---------------------------------------------------------------------------
# Repositorio de Artifact Registry (frontend + 2 microservicios)
# ---------------------------------------------------------------------------

resource "google_artifact_registry_repository" "imagenes" {
  location      = var.region
  repository_id = var.equipo
  description   = "Imagenes del proyecto final - equipo ${var.equipo}"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}

# ---------------------------------------------------------------------------
# Cuenta de servicio de los nodos, con permiso de LECTURA sobre el repositorio.
# Evita el ImagePullBackOff al desplegar.
# ---------------------------------------------------------------------------

resource "google_service_account" "nodos" {
  account_id   = "nodos-${var.equipo}"
  display_name = "Nodos GKE - equipo ${var.equipo}"

  depends_on = [google_project_service.apis]
}

resource "google_artifact_registry_repository_iam_member" "nodos_lectura" {
  project    = google_artifact_registry_repository.imagenes.project
  location   = google_artifact_registry_repository.imagenes.location
  repository = google_artifact_registry_repository.imagenes.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.nodos.email}"
}

# ---------------------------------------------------------------------------
# Cluster GKE Standard zonal
# ---------------------------------------------------------------------------

resource "google_container_cluster" "lab" {
  name     = var.nombre_cluster
  location = var.zona

  # Se elimina el grupo de nodos que GKE crea por omision, para administrar
  # el grupo con el recurso de abajo.
  remove_default_node_pool = true
  initial_node_count       = 1

  # Sin esto el destroy falla.
  deletion_protection = false

  depends_on = [google_project_service.apis]
}

# ---------------------------------------------------------------------------
# Node pool: 2 nodos e2-small de tipo spot
# ---------------------------------------------------------------------------

resource "google_container_node_pool" "nodos" {
  name     = "pool-${var.equipo}"
  cluster  = google_container_cluster.lab.name
  location = google_container_cluster.lab.location

  node_count = 2

  node_config {
    machine_type    = "e2-small"
    spot            = true
    disk_size_gb    = 30
    service_account = google_service_account.nodos.email
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  depends_on = [google_artifact_registry_repository_iam_member.nodos_lectura]
}
