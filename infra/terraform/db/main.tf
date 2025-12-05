terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

resource "docker_container" "postgres" {
  name  = var.db_host
  image = "postgres:15"
  env = [
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_pass}",
    "POSTGRES_DB=${var.db_name}"
  ]
  ports {
    internal = var.db_port
    external = var.db_port
  }
  networks_advanced {
    name = var.network_name
    aliases = [ var.db_host ]
  }
}
