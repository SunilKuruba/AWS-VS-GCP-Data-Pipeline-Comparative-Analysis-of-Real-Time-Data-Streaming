resource "google_managed_kafka_cluster" "kafka" {
  provider    = google-beta
  name        = var.cluster_id
  location    = var.region

  gcp_config {
    project = var.project_id
    network = var.subnet_self_link
  }

  capacity {
    vcpu_count   = 2
    memory_bytes = 4294967296  # 4 GB
  }

  kafka_config {
    version = "3.7.2" # or whatever version you want
  }

  billing_config {
    billing_mode = "PAY_AS_YOU_GO"
  }
}

resource "google_managed_kafka_topic" "iot_topic" {
  provider             = google-beta
  name                 = var.kafka_topic
  cluster              = google_managed_kafka_cluster.kafka.name
  location             = var.region
  topic_id             = var.kafka_topic
  partition_count      = 1
  replication_factor   = 1
}
