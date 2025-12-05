variable "project_root_path" {
  description = "Absolute path to project root"
  type        = string
  default     = "Users/username/path/to/project"
}

variable "network_name" {
  description = "Name of the Docker network"
  type        = string
}

variable "db_port" {
  type = string
}

variable "db_host" {
  type = string
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

variable "dbt_dataset" {
  type = string
}

variable "dbt_dev_name" {
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

variable "spotify_refresh_token" {
  type = string
}

variable "spotify_scopes" {
  type = string
}

variable "kafka_bootstrap_servers" {
  type = string
}

variable "kafka_topic" {
  type = string
}

variable "poll_interval" {
  type = string
}
