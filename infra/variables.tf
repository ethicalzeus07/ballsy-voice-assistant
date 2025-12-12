variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "ballsy-voice-assistant"
}

variable "artifact_registry_repo" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "ballsy-backend"
}

variable "image_name" {
  description = "Docker image name"
  type        = string
  default     = "ballsy-voice-assistant"
}

variable "cors_origins" {
  description = "Comma-separated list of allowed CORS origins"
  type        = string
  default     = "*"
}

variable "db_instance_name" {
  description = "Cloud SQL instance name"
  type        = string
  default     = "ballsy-db"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "ballsydb"
}

variable "db_user" {
  description = "Database user name"
  type        = string
  default     = "ballsyuser"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 3
}

variable "cpu" {
  description = "CPU allocation for Cloud Run"
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory allocation for Cloud Run (e.g., '2Gi')"
  type        = string
  default     = "2Gi"
}

variable "concurrency" {
  description = "Maximum concurrent requests per instance"
  type        = number
  default     = 10
}

