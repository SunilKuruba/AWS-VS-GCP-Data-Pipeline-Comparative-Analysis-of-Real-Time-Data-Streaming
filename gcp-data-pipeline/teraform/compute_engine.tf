resource "google_compute_instance" "vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "projects/debian-cloud/global/images/debian-12-bookworm-v20240415"
    }
  }

  network_interface {
    subnetwork    = var.subnet_self_link
    access_config {}
  }

  service_account {
    email  = "default"
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    set -eux

    # Install dependencies
    apt-get update
    apt-get install -y python3-pip python3-venv git

    python3 -m venv /opt/venv
    /opt/venv/bin/pip install --upgrade pip
    /opt/venv/bin/pip install confluent_kafka apache-beam[gcp] google-cloud-bigtable google-auth urllib3

    mkdir -p /opt/pipeline
    cd /opt/pipeline

    # Clone your repository
    git clone https://github.com/SunilKuruba/aws-vs-gcp-data-pipeline.git
    cd aws-vs-gcp-data-pipeline/gcp-data-pipeline

    # Launch publisher.py
    nohup /opt/venv/bin/python publisher.py \
      --bootstrap-servers=${var.bootstrap_server} \
      --topic-name=${var.kafka_topic} \
      --num_messages=100 \
      --delay=0.2 >/var/log/publisher.log 2>&1 &

    # Launch beam_processing.py
    nohup /opt/venv/bin/python beam_processing.py >/var/log/beam.log 2>&1 &
  EOF
}
