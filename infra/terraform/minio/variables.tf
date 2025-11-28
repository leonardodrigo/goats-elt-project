variable "minio_root_user" {
  type = string
}

variable "minio_root_password" {
  type      = string
  sensitive = true
}

variable "minio_default_bucket" {
  type = string
}

variable "network_name" {
  description = "Name of the Docker network"
  type        = string
}
