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
    context = "${var.project_root_path}/infra"
  }
#   triggers = {
#     dir_sha1 = sha1(join("", [for f in fileset(var.project_root_path, "src/*") : filesha1(f)]))
#   }
}

resource "docker_container" "elt-container" {
  name  = "elt-container"
  image = docker_image.elt-image.image_id
  ports {
    internal = 8080
    external = 8080
  }
  env = [
    "DB_PORT=5432",
    "DB_USER=${var.db_user}",
    "DB_PASSWORD=${var.db_pass}",
    "DB_NAME=${var.db_name}",
    "DB_URL=postgres://${var.db_user}:${var.db_pass}@postgres:5432/${var.db_name}"
  ]
}

output "docker_image_id" {
    value = docker_image.elt-image.image_id
}