terraform {
  backend "gcs" {
    bucket = "goats-elt-tfstate"
    prefix = "gcp/dev"
  }
}
