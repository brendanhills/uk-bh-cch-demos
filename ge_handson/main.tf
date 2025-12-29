
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.51.0"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  billing_project = var.project_id
  user_project_override = true
}

resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "datastore" {
  name          = "${var.bucket_name}-${random_id.bucket_prefix.hex}"
  location      = var.location
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_discovery_engine_data_store" "datastore" {
  project             = var.project_id
  location            = var.location
  data_store_id       = "datastore-${random_id.bucket_prefix.hex}"
  display_name        = "datastore-${random_id.bucket_prefix.hex}"
  solution_types      = ["SOLUTION_TYPE_SEARCH"]
  content_config      = "NO_CONTENT"
  create_advanced_site_search = false
  industry_vertical           = "GENERIC"
}

output "bucket_name" {
  value = google_storage_bucket.datastore.name
}

output "data_store_id" {
  value = google_discovery_engine_data_store.datastore.data_store_id
}

output "project_id" {
  value = var.project_id
}

output "location" {
  value = var.location
}
