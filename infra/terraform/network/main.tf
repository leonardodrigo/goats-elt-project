terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

resource "docker_network" "elt_net" {
  name = "elt_net"
}

output "network_name" {
  value = docker_network.elt_net.name
}
