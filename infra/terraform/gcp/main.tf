locals {
  project_id = var.project_id
  env        = var.environment
  prefix     = "goats-elt"

  streamlit_service_name = "${local.prefix}-streamlit-${local.env}"
  streamlit_repo_id      = "${local.prefix}-apps-${local.env}"
  streamlit_image_name   = "${local.prefix}-streamlit"
}

# Enable core APIs
resource "google_project_service" "services" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    # "run.googleapis.com",
    # "artifactregistry.googleapis.com",
  ])

  project = local.project_id
  service = each.value

  disable_on_destroy = false
}

# Spotify raw bucket
resource "google_storage_bucket" "spotify_raw" {
  name                        = "${local.prefix}-spotify-raw-${local.env}"
  project                     = local.project_id
  location                    = var.location
  uniform_bucket_level_access = true

  labels = {
    env       = local.env
    component = "elt"
    source    = "spotify"
  }
}

# Runtime service account for ELT
resource "google_service_account" "spotify_elt" {
  account_id   = "spotify-elt"
  display_name = "Spotify ELT runtime SA"
}

# Give Spotify ELT runtime SA read/write on the Spotify raw bucket
resource "google_storage_bucket_iam_member" "spotify_elt_storage_rw" {
  bucket = google_storage_bucket.spotify_raw.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.spotify_elt.email}"
}

# # Artifact registry to save streamlit image
# resource "google_artifact_registry_repository" "streamlit_repo" {
#   location      = var.region
#   repository_id = local.streamlit_repo_id
#   description   = "Artifact Registry for Streamlit app"
#   format        = "DOCKER"

#   labels = {
#     env       = local.env
#     component = "streamlit"
#   }
# }

# Service account for Cloud Run
resource "google_service_account" "streamlit_sa" {
  account_id   = "streamlit-${local.env}"
  display_name = "Streamlit Cloud Run SA (${local.env})"
}

resource "google_project_iam_member" "streamlit_sa_artifact_reader" {
  project = local.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.streamlit_sa.email}"
}

# Service account for GitHub Actions deployments
resource "google_service_account" "github_actions_deployer" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions Deployer (${local.env})"
}

# Allow GitHub Actions SA to manage Cloud Run
resource "google_project_iam_member" "gha_run_admin" {
  project = local.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

# Allow GitHub Actions SA to push images to Artifact Registry
resource "google_project_iam_member" "gha_artifact_writer" {
  project = local.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

# Allow GitHub Actions SA to *use* the Streamlit runtime SA
resource "google_service_account_iam_member" "gha_can_use_streamlit_sa" {
  service_account_id = google_service_account.streamlit_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.github_actions_deployer.email}"
}

# Cloud Run V2 service
# resource "google_cloud_run_v2_service" "streamlit" {
#   name     = local.streamlit_service_name
#   location = var.region

#   deletion_protection = false

#   template {
#     service_account = google_service_account.streamlit_sa.email

#     containers {
#       image = "${var.region}-docker.pkg.dev/${local.project_id}/${local.streamlit_repo_id}/${local.streamlit_image_name}:${var.streamlit_image_tag}"

#       resources {
#         limits = {
#           cpu    = "1"
#           memory = "1Gi"
#         }
#       }

#       ports {
#         container_port = 8080
#       }
#     }
#   }

#   ingress = "INGRESS_TRAFFIC_ALL"

#   lifecycle {
#     ignore_changes = [
#       template[0].containers[0].image
#     ]
#   }
# }


# # Public access to app
# resource "google_cloud_run_v2_service_iam_member" "streamlit_public" {
#   location = google_cloud_run_v2_service.streamlit.location
#   name     = google_cloud_run_v2_service.streamlit.name
#   role     = "roles/run.invoker"
#   member   = "allUsers"
# }

# # Output of App
# output "streamlit_url" {
#   value       = google_cloud_run_v2_service.streamlit.uri
#   description = "Public URL of the Streamlit app"
# }
