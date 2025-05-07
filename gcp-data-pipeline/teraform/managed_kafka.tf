variable "create_kafka_cluster" {
  type    = bool
  default = true
}

resource "google_managed_kafka_cluster" "kafka" {
  count      = var.create_kafka_cluster ? 1 : 0
  provider   = google-beta
  cluster_id = var.cluster_id
  location   = var.region

  capacity_config {
    vcpu_count   = 4
    memory_bytes = 8589934592
  }

  gcp_config {
    access_config {
      network_configs {
        subnet = var.subnet_self_link
      }
    }
  }
}

resource "google_managed_kafka_topic" "iot-topic" {
  count              = var.create_kafka_cluster ? 1 : 0
  provider           = google-beta
  cluster            = google_managed_kafka_cluster.kafka[0].cluster_id
  location           = var.region
  topic_id           = var.kafka_topic
  partition_count    = 1
  replication_factor = 3
}
