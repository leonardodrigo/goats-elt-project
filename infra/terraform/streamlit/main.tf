terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

resource "docker_image" "streamlit-image" {
  name = "streamlit-image"
  build {
    context    = var.project_root_path
    dockerfile = "infra/terraform/streamlit/Dockerfile"
  }
  #   triggers = {
  #     dir_sha1 = sha1(join("", [for f in fileset(var.project_root_path, "src/*") : filesha1(f)]))
  #   }
}

resource "docker_container" "streamlit-service" {
  name  = "streamlit-service"
  image = docker_image.streamlit-image.image_id
  ports {
    internal = 8080
    external = 8090
  }
  env = [
    "DATABASE_URL=postgres://${var.db_user}:${var.db_pass}@${var.db_host}:${var.db_port}/${var.db_name}",
  ]
}

output "docker_image_id" {
  value = docker_image.streamlit-image.image_id
}
