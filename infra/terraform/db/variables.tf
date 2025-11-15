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

variable "network_name" {
  type = string
}
