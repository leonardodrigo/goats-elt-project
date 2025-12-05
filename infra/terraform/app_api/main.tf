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
    context    = var.project_root_path
    dockerfile = "infra/terraform/app_api/Dockerfile"
  }
  #   triggers = {
  #     dir_sha1 = sha1(join("", [for f in fileset(var.project_root_path, "src/*") : filesha1(f)]))
  #   }
}

resource "docker_container" "elt-service" {
  name  = "elt-service"
  image = docker_image.elt-image.image_id
  ports {
    internal = 8080
    external = 8080
  }
  env = [
    "POSTGRES_HOST=${var.db_host}",
    "POSTGRES_PORT=${var.db_port}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_pass}",
    "POSTGRES_DB=${var.db_name}",
    "DBT_DATASET=${var.dbt_dataset}",
    "DBT_DEV_NAME=${var.dbt_dev_name}",
    "SPOTIPY_CLIENT_ID=${var.spotify_client_id}",
    "SPOTIPY_CLIENT_SECRET=${var.spotify_client_secret}",
    "SPOTIPY_REDIRECT_URI=${var.spotify_redirect_uri}",
    "SPOTIPY_REFRESH_TOKEN=${var.spotify_refresh_token}",
    "SPOTIPY_SCOPES=${var.spotify_scopes}",
    "KAFKA_BOOTSTRAP_SERVERS=${var.kafka_bootstrap_servers}",
    "KAFKA_TOPIC=${var.kafka_topic}",
    "POLL_INTERVAL=${var.poll_interval}"
  ]
  networks_advanced {
    name = var.network_name
  }
}

output "docker_image_id" {
  value = docker_image.elt-image.image_id
}
