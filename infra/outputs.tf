output "cloud_run_url" {
  description = "URL of the Cloud Run service"
  value       = google_cloud_run_v2_service.main.uri
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = google_cloud_run_v2_service.main.name
}

output "database_instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.main.connection_name
  sensitive   = false
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.main.name
}

output "database_user" {
  description = "Database user name"
  value       = google_sql_user.main.name
}

output "database_password" {
  description = "Database password (auto-generated)"
  value       = random_password.db_password.result
  sensitive   = true
}

output "artifact_registry_url" {
  description = "Full Artifact Registry image URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repo}/${var.image_name}"
}

output "gemini_secret_name" {
  description = "Secret Manager secret name for Gemini API key"
  value       = google_secret_manager_secret.gemini_api_key.secret_id
}

output "database_url_secret_name" {
  description = "Secret Manager secret name for database URL"
  value       = google_secret_manager_secret.database_url.secret_id
}

