# Artifact Registry for Docker images

resource "google_artifact_registry_repository" "backend" {
  location      = var.region
  repository_id = var.artifact_registry_repo
  description   = "Docker repository for Ballsy Voice Assistant"
  format        = "DOCKER"

  depends_on = [google_project_service.artifact_registry]
}

