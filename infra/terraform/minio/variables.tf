variable "minio_root_user" {
  type = string
}

variable "minio_root_password" {
  type      = string
  sensitive = true
}

variable "network_name" {
  description = "Name of the Docker network"
  type        = string
}
