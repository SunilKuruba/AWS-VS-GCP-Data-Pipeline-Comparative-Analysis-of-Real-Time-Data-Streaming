variable "project_id" {
  type    = string
  default = "cool-continuity-457614-b2"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "subnet_self_link" {
  type = string
}

variable "vm_name" {
  type    = string
  default = "pipeline-vm"
}

variable "machine_type" {
  type    = string
  default = "e2-medium"
}

# Bigtable
variable "bootstrap_server" {
  type = string
}

variable "kafka_topic" {
  type    = string
  default = "iot-data"
}

# Kafka (already provisioned)
variable "bt_instance_id" {
  type    = string
  default = "iot-data-store"
}

variable "bt_table_id" {
  type    = string
  default = "weather-info"
}
