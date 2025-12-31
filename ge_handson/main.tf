terraform {
  required_providers {
    google = {
      source  = "hashicorp/google-beta"
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

resource "google_discovery_engine_data_store" "gcs_datastore" {
  project             = var.project_id
  location            = var.location
  data_store_id       = "datastore-${random_id.resource_prefix.hex}"
  display_name        = "datastore-${random_id.resource_prefix.hex}"
  solution_types      = ["SOLUTION_TYPE_SEARCH"]
  content_config      = "CONTENT_REQUIRED"
  create_advanced_site_search = false
  industry_vertical           = "GENERIC"
}

resource "google_discovery_engine_search_engine" "gemini_enterprise_search_engine" {
  engine_id                   = "ge-engine-${random_id.resource_prefix.hex}"
  collection_id               = "default_collection"
  location                    = var.location
  display_name                = "ge-handson-search-engine"
  project                     = var.project_id
  data_store_ids = [
    google_discovery_engine_data_store.gcs_datastore.data_store_id,
    # The data store ID for a connector is its collection_id + "_" + its data_source
    # format("%s_%s", google_discovery_engine_data_connector.gmail.collection_id, google_discovery_engine_data_connector.gmail.data_source),
    # format("%s_%s", google_discovery_engine_data_connector.google_drive.collection_id, google_discovery_engine_data_connector.google_drive.data_source),
  ]
  industry_vertical           = "GENERIC"
  app_type                    = "APP_TYPE_INTRANET"
  search_engine_config {
  }
}

output "data_store_id" {
  value = google_discovery_engine_data_store.gcs_datastore.data_store_id
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