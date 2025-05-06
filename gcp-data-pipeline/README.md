
# GCP IoT Data Pipeline

This project builds a real-time data processing pipeline on **Google Cloud Platform (GCP)** using **Managed Kafka**, **Apache Beam**, and **Bigtable**. It simulates ingestion of weather-related IoT data, publishes it to a Kafka topic, processes the data using Apache Beam, and optionally stores the enriched results in Bigtable.

---

## Project Structure

```bash
gcp-data-pipeline/
├── terraform/                    # Terraform scripts to automate GCP infra setup
│   ├── bigtable.tf               # Creates Bigtable instance, table, and column family
│   ├── compute_engine.tf         # Creates a new VM instance
│   ├── iam.tf                    # IAM roles and bindings
│   ├── main.tf                   # Terraform entry point
│   ├── managed_kafka.tf          # Managed Kafka cluster and topic creation
│   ├── variables.tf              # Input variables used across Terraform configs
│   ├── versions.tf               # Provider and Terraform version constraints
├── beam_processing.py            # Apache Beam consumer pipeline
├── data_ingestion.py             # Kafka event producer
└── README.md                     # Documentation (this file)
```



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
     terraform validate
     terraform plan -var="create_kafka_cluster=false" -out=tfplan.out
     terraform apply tfplan.out -auto-approve
     ```
4. ** To destroy the PipeLine**
     ```
     terraform destroy -auto-approve
     ```






