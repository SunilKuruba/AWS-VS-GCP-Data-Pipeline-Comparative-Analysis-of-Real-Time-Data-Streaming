/* provider "google" {
  project = var.project_id
  region  = "us-us-central1"
  zone    = "us-us-central1-f"
}

# Variables (you can define these in a variables.tf or .tfvars file)
variable "project_id" {}
variable "subnet_path" {}

# Create a Compute Engine instance
resource "google_compute_instance" "test_instance" {
  name         = "test-instance"
  machine_type = "e2-medium"
  zone         = "us-us-central1-f"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = var.subnet_path
    access_config {}
  }

  service_account {
    email  = "${var.project_number}-compute@developer.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  tags = ["kafka-client"]
}

# Grant IAM role to the default compute service account
resource "google_project_iam_member" "compute_sa_managedkafka" {
  project = var.project_id
  role    = "roles/managedkafka.client"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}

*/ 

terraform {
  required_version = ">= 1.6"
  required_providers {
    google = { source = "hashicorp/google", version = ">= 6.26" }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
