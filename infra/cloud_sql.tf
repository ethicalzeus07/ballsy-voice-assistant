# Cloud SQL PostgreSQL instance

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "google_sql_database_instance" "main" {
  name             = var.db_instance_name
  database_version  = "POSTGRES_15"
  region           = var.region

  settings {
    tier              = "db-f1-micro"  # Smallest/cheapest tier
    availability_type = "ZONAL"
    
    disk_size       = 20
    disk_type       = "PD_SSD"
    disk_autoresize = true

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled = false  # Use private IP only
      private_network = null
    }
  }

  deletion_protection = false  # Set to true in production

  depends_on = [google_project_service.sql_admin]
}

resource "google_sql_database" "main" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

