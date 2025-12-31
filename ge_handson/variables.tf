variable "project_id" {
  description = "The project ID to deploy to."
  type        = string
}

variable "region" {
  description = "The region to deploy to."
  type        = string
}

variable "location" {
  description = "The location to deploy to."
  type        = string
}

variable "gcs_data_store_id" {
  description = "The ID of the GCS data store created by the Python script."
  type        = string
}

variable "gdrive_data_store_id" {
  description = "The ID of the Google Drive data store created by the Python script."
  type        = string
}