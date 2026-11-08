variable "project_id" {
  description = "Identificador del proyecto de Google Cloud (sin valor por defecto: se pasa en terraform.tfvars)"
  type        = string
}

variable "region" {
  description = "Region de Google Cloud (Artifact Registry y provider)"
  type        = string
  default     = "us-central1"
}

variable "zona" {
  description = "Zona del cluster GKE zonal (debe pertenecer a la region)"
  type        = string
  default     = "us-central1-a"
}

variable "equipo" {
  description = "Identificador del equipo. Se usa en el repositorio, el node pool y la cuenta de servicio."
  type        = string
  default     = "holdovers"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.equipo))
    error_message = "El identificador del equipo debe iniciar con letra y usar solo minusculas, numeros y guiones (3 a 21 caracteres)."
  }
}

variable "nombre_cluster" {
  description = "Nombre del cluster GKE (lleva el identificador del equipo)"
  type        = string
  default     = "holdovers-gke"
}
