/* 
# IAM role to the default compute service account
resource "google_project_iam_member" "compute_sa_managedkafka" {
  project = var.project_id
  role    = "roles/managedkafka.client"
  member  = "serviceAccount:${var.project_number}-compute@developer.gserviceaccount.com"
}
*/