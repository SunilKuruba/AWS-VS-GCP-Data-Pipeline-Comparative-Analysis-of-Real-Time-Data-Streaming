
# GCP IoT Data Pipeline

This project builds a real-time data processing pipeline on **Google Cloud Platform (GCP)** using **Managed Kafka**, **Apache Beam**, and **Bigtable**. It simulates ingestion of weather-related IoT data, publishes it to a Kafka topic, processes the data using Apache Beam, and optionally stores the enriched results in Bigtable.

### GCP Resources Summary

This table outlines the Google Cloud resources declared in Terraform and how they support each stage of the pipeline (Ingest → Process → Store).

| Category | Resource Type | Name (Terraform) | Key Specifications / Purpose |
|----------|-------------------------------|------------------|------------------------------|
| **IAM** | `google_project_iam_member` | `compute_sa_managedkafka` | Grants `roles/managedkafka.client` to the default Compute Engine service account so the VM can interact with Managed Kafka. |
| **Compute VM ** | `google_compute_instance` | `vm` | Debian 12, `machine_type = var.machine_type`, subnet = `var.subnet_self_link`, external IP enabled. Startup script installs Python, clones the repo, and runs `data_ingestion.py` and `beam_processing.py`. |
| **Kafka** | `google_managed_kafka_cluster` | `kafka` | 4 vCPUs, 8 GiB RAM, region = `var.region`, subnet = `var.subnet_self_link`. |
| | `google_managed_kafka_topic` | `iot_topic` | Partitions = 1, Replication factor = 3. Used to transport IoT data from the VM to the processing step. |
| **Beam** | *(Beam job launched from VM)* | — | Apache Beam (Dataflow runner). Job is triggered by `beam_processing.py` on the VM. Transforms Kafka messages. |
| **Bigtable** | `google_bigtable_instance` | `bt_instance` | Single-node, HDD storage, `zone = var.zone`, `environment = prod`. |
| | `google_bigtable_table` | `bt_table` | Column family `cf1`, `deletion_protection = false`. Table resides in the Bigtable instance and stores processed data. |


<!-- <img width="669" alt="image" src="https://github.com/user-attachments/assets/4048d3d1-00d4-42c7-91a4-8d24f54c07f0" /> -->

<img width="669" alt="image" src="https://github.com/user-attachments/assets/12909296-0cc1-4670-bac8-548cb45c4973" />




---

## How to Run This Project

### Step 1: Set Up GCP Resources

1. **Create a GCP project** (if you don’t have one already)
2.  **Create Kafka Cluster**
    - Create a kafka-cluster and note down the Bootstrap Address
    - Create Kafka-topic  
3. **Enable the following APIs**:
   - Managed Kafka (Confluent Cloud or GCP Marketplace offering)
   - Bigtable Admin API
   - IAM & OAuth2
4. **Create a Bigtable instance and table**:
   - Instance ID: `iot-data-store`
   - Table ID: `weather-info`
   - Column family: `cf1`
5. **Ceate a VM Instance**:
    

### Step 2: Install Dependencies into the VM Instance

``` bash
pip install confluent-kafka apache-beam[gcp] google-cloud-bigtable
```

To Start producing events run the below script

```
nohup /opt/venv/bin/python data_ingestion.py \
      --bootstrap-servers=${var.bootstrap_server} \
      --topic-name=${var.kafka_topic} \
      --num_messages=2 \
      --delay=5 >/var/log/publisher.log 2>&1 &
```

To start the pipeline start the script 
```
nohup /opt/venv/bin/python beam_processing.py >/var/log/beam.log 2>&1 &
```

The above 2 scripts will start the whole pipeline and log the data into their respective log files.




## Creating the pipeline using teraform script

1. **Clone the github repo into an existing vm in GCP**
2. **Go to the terraform path**
3. ** Run the below script**
     ```
     cd terraform
     terraform init
     terraform plan -out=tfplan.out
     terraform apply tfplan.out
     ```
4. ** To destroy the PipeLine**
     ```
     terraform destroy
     ```






