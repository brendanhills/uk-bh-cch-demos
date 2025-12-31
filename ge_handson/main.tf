terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.14.0"
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


resource "random_uuid" "run_id" {}

resource "random_uuid" "run_id_2" {}

resource "random_id" "resource_prefix" {
  byte_length = 8
  # Add a keeper that changes on each run after a destroy.
  # This forces a new random_id, preventing name collisions with recently
  # deleted Discovery Engine resources.
  keepers = { run_id = random_uuid.run_id_2.result }
}

resource "google_discovery_engine_search_engine" "gemini_enterprise_search_engine" {
  engine_id                   = "ge-engine-${random_id.resource_prefix.hex}"
  collection_id               = "default_collection"
  location                    = var.location
  display_name                = "ge-handson-search-engine"
  project                     = var.project_id
  data_store_ids = [
    var.gcs_data_store_id,
    var.gdrive_data_store_id,
  ]
  industry_vertical           = "GENERIC"
  app_type                    = "APP_TYPE_INTRANET"
  search_engine_config {
  }
}

output "project_id" {
  value = var.project_id
}

output "location" {
  value = var.location
}

output "search_engine_id" {
  value = google_discovery_engine_search_engine.gemini_enterprise_search_engine.engine_id
}
