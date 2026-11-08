output "comando_credenciales" {
  description = "Comando para configurar kubectl contra el cluster"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.lab.name} --zone ${google_container_cluster.lab.location} --project ${var.project_id}"
}

output "repositorio" {
  description = "Identificador del repositorio de Artifact Registry"
  value       = google_artifact_registry_repository.imagenes.id
}

output "ruta_imagenes" {
  description = "Prefijo para etiquetar las imagenes: <ruta_imagenes>/<imagen>:<tag>"
  value       = "${google_artifact_registry_repository.imagenes.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.imagenes.repository_id}"
}
