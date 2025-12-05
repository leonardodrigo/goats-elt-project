terraform {
  backend "gcs" {
    bucket = "goats-elt-tfstate"
    prefix = "gcp/dev"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.8.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
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

module "app" {
  source                = "./app"
  depends_on            = [module.db]
  project_root_path     = var.project_root_path
  network_name          = module.network.network_name
  db_user               = var.db_user
  db_pass               = var.db_pass
  db_name               = var.db_name
  spotify_client_id     = var.spotify_client_id
  spotify_client_secret = var.spotify_client_secret
  spotify_redirect_uri  = var.spotify_redirect_uri
}

output "spotify_redirect_uri" {
  value = var.spotify_redirect_uri
}

module "gcp" {
  source      = "./gcp"
  project_id  = var.project_id
  region      = var.region
  location    = var.location
  environment = var.environment

}
