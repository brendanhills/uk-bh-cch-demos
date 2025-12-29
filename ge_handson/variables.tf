
variable "project_id" {
  description = "The GCP project ID."
  type        = string
}

variable "region" {
  description = "The GCP region."
  type        = string
}

variable "location" {
  description = "The GCP location for the GCS bucket."
  type        = string
}

variable "bucket_name" {
  description = "The name of the GCS bucket."
  type        = string
  default     = "gemini-datastore"
}
