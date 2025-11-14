terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

module "network" {
  source = "./network"
}

module "db" {
  source       = "./db"
  network_name = module.network.network_name
  db_user      = var.db_user
  db_pass      = var.db_pass
  db_name      = var.db_name
}

module "minio" {
  source       = "./minio"
  network_name = module.network.network_name
  minio_user   = var.minio_user
  minio_pass   = var.minio_pass
}

module "app" {
  source            = "./app"
  project_root_path = var.project_root_path
  network_name      = module.network.network_name
  db_user           = var.db_user
  db_pass           = var.db_pass
  db_name           = var.db_name
}
