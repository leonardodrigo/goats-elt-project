locals {
  project_id = var.project_id
  env        = var.environment
  prefix     = "goats-elt"
}

# Enable core APIs
resource "google_project_service" "services" {
  for_each = toset([
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    # Can use below later
    # "run.googleapis.com",
    # "artifactregistry.googleapis.com",
    # "sqladmin.googleapis.com",
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
