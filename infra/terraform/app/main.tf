terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

resource "docker_image" "elt-image" {
  name = "elt-image"
  build {
    context = var.project_root_path
    dockerfile = "infra/terraform/app/Dockerfile"
  }
#   triggers = {
#     dir_sha1 = sha1(join("", [for f in fileset(var.project_root_path, "src/*") : filesha1(f)]))
#   }
}

resource "docker_container" "elt-container" {
  name  = "elt-container"
  image = docker_image.elt-image.image_id
  env = [
    "DATABASE_URL=postgres://${var.db_user}:${var.db_pass}@postgres:5432/${var.db_name}",
    "MINIO_ACCESS_KEY=${var.minio_root_user}",
    "MINIO_SECRET_KEY=${var.minio_root_password}",
    "MINIO_DEFAULT_BUCKET=${var.minio_default_bucket}",
    "SPOTIPY_CLIENT_ID=${var.spotify_client_id}",
    "SPOTIPY_CLIENT_SECRET=${var.spotify_client_secret}",
    "SPOTIPY_REDIRECT_URI=${var.spotify_redirect_uri}"
  ]
}

output "docker_image_id" {
    value = docker_image.elt-image.image_id
}