# Uncomment to create.  If the cluster already exists, run `terraform import`.
/*
resource "google_managed_kafka_cluster" "kafka" {
  provider        = google-beta
  cluster_id      = var.cluster_id
  location        = var.region               # regional cluster
  encryption_key  = "google-managed"         # default CMEK
  # Network section uses the subnet you passed in
  network_config {
    subnet = var.subnet_self_link
  }
  capacity_config {
    # Example: 3-node, 2 vCPU each
    per_broker_cpu   = 2
    per_broker_count = 3
  }
}

resource "google_managed_kafka_topic" "iot_topic" {
  provider    = google-beta
  name        = var.topic_name
  cluster_id  = google_managed_kafka_cluster.kafka.cluster_id
  location    = var.region
  partitions  = 6
}
*/
