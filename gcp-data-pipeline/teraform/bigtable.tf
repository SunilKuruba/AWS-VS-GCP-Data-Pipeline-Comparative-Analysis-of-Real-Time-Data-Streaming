resource "google_bigtable_instance" "bt_instance" {
  name          = var.bt_instance_id

  cluster {
    cluster_id   = "${var.bt_instance_id}-cluster"
    zone         = var.zone
    num_nodes    = 1
    storage_type = "HDD"
  }

  labels = {
    environment = "prod"
  }
}

resource "google_bigtable_table" "bt_table" {
  name          = var.bt_table_id
  instance_name = google_bigtable_instance.bt_instance.name

  column_family {
    family = "cf1"
  }
}
