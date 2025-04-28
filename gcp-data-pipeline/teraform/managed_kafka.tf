/* 

resource "google_managed_kafka_cluster" "kafka" {
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

resource "google_managed_kafka_topic" "iot_topic" {
  provider           = google-beta
  cluster            = google_managed_kafka_cluster.kafka.cluster_id
  location           = var.region

  topic_id           = var.kafka_topic
  partition_count    = 1
  replication_factor = 3
}

*/