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
  source                = "./minio"
  network_name          = module.network.network_name
  minio_root_user       = var.minio_root_user
  minio_root_password   = var.minio_root_password
}

module "app" {
  source               = "./app"
  depends_on = [ module.minio, module.db ]
  project_root_path    = var.project_root_path
  network_name         = module.network.network_name
  db_user              = var.db_user
  db_pass              = var.db_pass
  db_name              = var.db_name
  minio_root_user      = var.minio_root_user
  minio_root_password  = var.minio_root_password
  minio_default_bucket = var.minio_default_bucket
  spotify_client_id    = var.spotify_client_id
  spotify_client_secret= var.spotify_client_secret
  spotify_redirect_uri = var.spotify_redirect_uri
}

output "spotify_redirect_uri" {
  value = var.spotify_redirect_uri
}
