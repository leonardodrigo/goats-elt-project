variable "project_root_path" {
  description = "Absolute path to project root"
  type        = string
  default     = "Users/username/path/to/project"
}

variable "network_name" {
  description = "Name of the Docker network"
  type        = string
}

variable "db_user" {
  type = string
}

variable "db_pass" {
  type      = string
  sensitive = true
}

variable "db_name" {
  type = string
}

variable "spotify_client_id" {
  type = string
}

variable "spotify_client_secret" {
  type = string
}

variable "spotify_redirect_uri" {
  type = string
}

variable "project_id" {
  description = "GCP project ID."
  type        = string
  default     = "goats-elt-project-478211"
}

variable "region" {
  description = "Default compute region."
  type        = string
  default     = "europe-west4"
}

variable "location" {
  description = "Default location for storage/BigQuery."
  type        = string
  default     = "EU"
}

variable "environment" {
  description = "Environment label (e.g. dev, prod)."
  type        = string
  default     = "dev"
}