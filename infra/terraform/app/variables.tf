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