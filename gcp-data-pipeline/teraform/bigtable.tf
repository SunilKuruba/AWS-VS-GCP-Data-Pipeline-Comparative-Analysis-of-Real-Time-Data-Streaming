resource "google_bigtable_instance" "iot" {
  name          = var.bigtable_instance_id
  instance_type = "PRODUCTION"
  cluster {
    cluster_id   = "${var.bigtable_instance_id}-c"
    zone         = var.zone
    num_nodes    = 1
    storage_type = "HDD"
  }
}

resource "google_bigtable_table" "weather" {
  instance_name = google_bigtable_instance.iot.name
  name          = var.bigtable_table_id
  column_family {
    family = "cf1"
  }
}
