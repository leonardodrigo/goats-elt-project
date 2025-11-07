variable "minio_user" {
    type = string
}

variable "minio_pass" {
    type = string
    sensitive = true
}

variable "network_name" {
  description = "Name of the Docker network"
  type        = string
}
