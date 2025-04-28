variable "project_id"       { type = string default = "cool-continuity-457614-b2"}
variable "region"           { type = string default = "us-central1" }
variable "zone"             { type = string default = "us-central1-f" }
variable "subnet_self_link" { type = string default = "projects/cool-continuity-457614-b2/regions/us-central1/subnetworks/default"}   # existing subnet
variable "vm_name"          { type = string default = "pipeline-vm" }
variable "machine_type"     { type = string default = "e2-medium" }

# Bigtable
variable "bt_instance_id" { type = string default = "iot-data-store" }
variable "bt_table_id"    { type = string default = "weather-info"}

# Kafka (already provisioned)
variable "bootstrap_server" { type = string default = "bootstrap.data-ingestion.us-central1.managedkafka.cool-continuity-457614-b2.cloud.goog:9092"}
variable "kafka_topic"      { type = string default = "iot-data" }
