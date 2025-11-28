terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

resource "docker_container" "goatminio" {
  name  = "minio"
  image = "minio/minio:latest"
  env = [
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}",
    "MINIO_DEFAULT_BUCKET=${var.minio_default_bucket}"
  ]
  command = ["server", "/data", "--console-address", ":9001"]
  ports {
    internal = 9000
    external = 9000
  }
  ports {
    internal = 9001
    external = 9001
  }
  networks_advanced { name = var.network_name }
}
