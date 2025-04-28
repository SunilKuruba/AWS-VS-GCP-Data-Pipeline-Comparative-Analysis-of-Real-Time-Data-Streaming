variable "project_id" {
  type    = string
  default = "cool-continuity-457614-b2"
}

variable "project_number" {
  type    = string
  default = "735481339104"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-f"
}

variable "subnet_self_link" {
  type = string
  default = "projects/cool-continuity-457614-b2/regions/us-central1/subnetworks/default"
}

# Kafka Config 

variable "cluster_id" {
  type    = string
  default = "data-ingestion-1"
}

variable "bootstrap_server" {
  type = string
  default = "bootstrap.data-ingestion-1.us-central1.managedkafka.cool-continuity-457614-b2.cloud.goog:9092"
}

variable "kafka_topic" {
  type    = string
  default = "iot-data"
}

# VM - Instance

variable "vm_name" {
  type    = string
  default = "pipeline-vm"
}

variable "machine_type" {
  type    = string
  default = "e2-medium"
}

# Bigtable
variable "bt_instance_id" {
  type    = string
  default = "iot-data-store-1"
}

variable "bt_table_id" {
  type    = string
  default = "weather-info"
}
