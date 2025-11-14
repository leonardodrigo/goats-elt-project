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

variable "minio_root_user" {
    type = string
}

variable "minio_root_password" {
    type = string
    sensitive = true
}

variable "minio_default_bucket" {
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
