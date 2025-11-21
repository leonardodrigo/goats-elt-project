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

variable "streamlit_image_tag" {
  description = "Tag for the Streamlit container image."
  type        = string
  default     = "dev"
}