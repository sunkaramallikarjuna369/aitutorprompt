# CBSE Learning Platform - GCP Infrastructure
# Terraform configuration for deploying the platform to Google Cloud Platform

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
    "firestore.googleapis.com",
    "redis.googleapis.com",
    "pubsub.googleapis.com",
    "aiplatform.googleapis.com",
    "identitytoolkit.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "cbse_learning" {
  location      = var.region
  repository_id = "cbse-learning"
  description   = "Container images for CBSE Learning Platform"
  format        = "DOCKER"
  
  depends_on = [google_project_service.services]
}

# Cloud SQL PostgreSQL instance
resource "google_sql_database_instance" "main" {
  name             = "cbse-learning-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier = var.db_tier
    
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }
    
    backup_configuration {
      enabled            = true
      start_time         = "03:00"
      point_in_time_recovery_enabled = true
    }
  }
  
  deletion_protection = var.deletion_protection
  
  depends_on = [google_project_service.services]
}

resource "google_sql_database" "cbse_learning" {
  name     = "cbse_learning"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "app_user" {
  name     = "cbse_app"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Firestore database (Native mode)
resource "google_firestore_database" "main" {
  provider    = google-beta
  name        = "(default)"
  location_id = var.firestore_location
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.services]
}

# Redis instance for caching
resource "google_redis_instance" "cache" {
  name           = "cbse-learning-cache"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  
  depends_on = [google_project_service.services]
}

# Pub/Sub topics for async events
resource "google_pubsub_topic" "quiz_submitted" {
  name = "quiz-submitted"
  
  depends_on = [google_project_service.services]
}

resource "google_pubsub_topic" "lesson_viewed" {
  name = "lesson-viewed"
  
  depends_on = [google_project_service.services]
}

resource "google_pubsub_topic" "progress_updated" {
  name = "progress-updated"
  
  depends_on = [google_project_service.services]
}

# Pub/Sub subscriptions
resource "google_pubsub_subscription" "quiz_submitted_progress" {
  name  = "quiz-submitted-progress-service"
  topic = google_pubsub_topic.quiz_submitted.name
  
  ack_deadline_seconds = 20
  
  push_config {
    push_endpoint = "${google_cloud_run_service.progress_service.status[0].url}/webhooks/quiz-submitted"
  }
}

resource "google_pubsub_subscription" "lesson_viewed_progress" {
  name  = "lesson-viewed-progress-service"
  topic = google_pubsub_topic.lesson_viewed.name
  
  ack_deadline_seconds = 20
  
  push_config {
    push_endpoint = "${google_cloud_run_service.progress_service.status[0].url}/webhooks/lesson-viewed"
  }
}

# Cloud Storage bucket for media
resource "google_storage_bucket" "media" {
  name          = "${var.project_id}-cbse-media"
  location      = var.region
  force_destroy = !var.deletion_protection
  
  uniform_bucket_level_access = true
  
  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD"]
    response_header = ["Content-Type"]
    max_age_seconds = 3600
  }
  
  depends_on = [google_project_service.services]
}

# Cloud Storage bucket for frontend (static hosting)
resource "google_storage_bucket" "frontend" {
  name          = "${var.project_id}-cbse-frontend"
  location      = var.region
  force_destroy = !var.deletion_protection
  
  uniform_bucket_level_access = true
  
  website {
    main_page_suffix = "index.html"
    not_found_page   = "index.html"
  }
  
  depends_on = [google_project_service.services]
}

resource "google_storage_bucket_iam_member" "frontend_public" {
  bucket = google_storage_bucket.frontend.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# Secret Manager secrets
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-key"
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = var.jwt_secret_key
}

resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.services]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

# Service Account for Cloud Run services
resource "google_service_account" "cloud_run" {
  account_id   = "cbse-learning-run"
  display_name = "CBSE Learning Platform Cloud Run Service Account"
}

resource "google_project_iam_member" "cloud_run_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/datastore.user",
    "roles/pubsub.publisher",
    "roles/secretmanager.secretAccessor",
    "roles/aiplatform.user",
    "roles/storage.objectViewer",
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Cloud Run service - Backend API
resource "google_cloud_run_service" "backend" {
  name     = "cbse-learning-backend"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/cbse-learning/backend:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.app_user.name}:${var.db_password}@/${google_sql_database.cbse_learning.name}?host=/cloudsql/${google_sql_database_instance.main.connection_name}"
        }
        
        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.cache.host
        }
        
        env {
          name  = "AI_PROVIDER"
          value = "vertex"
        }
        
        env {
          name  = "VERTEX_AI_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "VERTEX_AI_LOCATION"
          value = var.region
        }
        
        env {
          name = "JWT_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "1Gi"
          }
        }
      }
      
      container_concurrency = 80
      timeout_seconds       = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale"      = "10"
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.main.connection_name
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_project_service.services,
    google_secret_manager_secret_version.jwt_secret,
  ]
}

# Cloud Run service - Progress Service (for Pub/Sub webhooks)
resource "google_cloud_run_service" "progress_service" {
  name     = "cbse-learning-progress"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/cbse-learning/backend:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "SERVICE_MODE"
          value = "progress"
        }
        
        resources {
          limits = {
            cpu    = "1"
            memory = "512Mi"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.services]
}

# Allow unauthenticated access to backend
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow Pub/Sub to invoke progress service
resource "google_cloud_run_service_iam_member" "progress_pubsub" {
  service  = google_cloud_run_service.progress_service.name
  location = google_cloud_run_service.progress_service.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

data "google_project" "current" {}

# Cloud CDN for frontend
resource "google_compute_backend_bucket" "frontend" {
  name        = "cbse-frontend-backend"
  bucket_name = google_storage_bucket.frontend.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    default_ttl       = 3600
    max_ttl           = 86400
    client_ttl        = 3600
    negative_caching  = true
  }
}

# URL map for frontend
resource "google_compute_url_map" "frontend" {
  name            = "cbse-frontend-url-map"
  default_service = google_compute_backend_bucket.frontend.id
}

# Outputs
output "backend_url" {
  value       = google_cloud_run_service.backend.status[0].url
  description = "URL of the backend API"
}

output "frontend_bucket" {
  value       = google_storage_bucket.frontend.url
  description = "Frontend storage bucket URL"
}

output "database_connection" {
  value       = google_sql_database_instance.main.connection_name
  description = "Cloud SQL connection name"
  sensitive   = true
}

output "redis_host" {
  value       = google_redis_instance.cache.host
  description = "Redis instance host"
}

output "artifact_registry" {
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.cbse_learning.repository_id}"
  description = "Artifact Registry repository URL"
}
