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
  db_host      = var.db_host
  db_port      = var.db_port
  db_user      = var.db_user
  db_pass      = var.db_pass
  db_name      = var.db_name
}

module "minio" {
  source               = "./minio"
  network_name         = module.network.network_name
  minio_root_user      = var.minio_root_user
  minio_root_password  = var.minio_root_password
  minio_default_bucket = var.minio_default_bucket
}

module "streamlit" {
  source            = "./streamlit"
  depends_on        = [module.app_api]
  project_root_path = var.project_root_path
  network_name      = module.network.network_name
  db_user           = var.db_user
  db_pass           = var.db_pass
  db_name           = var.db_name
  db_port           = var.db_port
  db_host           = var.db_host
}

module "app_api" {
  source                  = "./app_api"
  depends_on              = [module.minio, module.db, module.kafka]
  project_root_path       = var.project_root_path
  network_name            = module.network.network_name
  db_host                 = var.db_host
  db_port                 = var.db_port
  db_user                 = var.db_user
  db_pass                 = var.db_pass
  db_name                 = var.db_name
  dbt_dataset             = var.dbt_dataset
  dbt_dev_name            = var.dbt_dev_name
  minio_endpoint          = var.minio_endpoint
  minio_root_user         = var.minio_root_user
  minio_root_password     = var.minio_root_password
  minio_default_bucket    = var.minio_default_bucket
  spotify_client_id       = var.spotify_client_id
  spotify_client_secret   = var.spotify_client_secret
  spotify_redirect_uri    = var.spotify_redirect_uri
  spotify_refresh_token   = var.spotify_refresh_token
  spotify_scopes          = var.spotify_scopes
  kafka_bootstrap_servers = var.kafka_bootstrap_servers
  kafka_topic             = var.kafka_topic
  poll_interval           = var.poll_interval
}

module "kafka" {
  source       = "./kafka"
  network_name = module.network.network_name
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
