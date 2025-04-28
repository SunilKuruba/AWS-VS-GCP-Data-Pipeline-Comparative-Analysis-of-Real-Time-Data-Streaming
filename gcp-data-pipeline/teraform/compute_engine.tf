resource "google_compute_instance" "vm" {
    name         = var.vm_name
    machine_type = var.machine_type
    zone         = var.zone
    tags         = ["kafka-beam"]

    boot_disk {
        initialize_params { image = "projects/debian-cloud/global/images/debian-12-bookworm-v20240415" }
    }

    network_interface {
        subnetwork    = var.subnet_self_link
        access_config {}                 # comment out to make the VM private-only
    }

    service_account {
        email  = google_service_account.sa.email
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    }

    metadata_startup_script = <<-EOF
    #!/usr/bin/env bash
    set -eux

    # ---------- 0. Variables from Terraform ----------
    BOOTSTRAP="${var.bootstrap_server}"
    TOPIC="${var.kafka_topic}"
    BT_INST="${var.bt_instance_id}"
    BT_TABLE="${var.bt_table_id}"

    # ---------- 1. System dependencies ----------
    apt-get update
    apt-get install -y python3-pip python3-venv git

    python3 -m venv /opt/venv
    /opt/venv/bin/pip install --upgrade pip
    /opt/venv/bin/pip install confluent_kafka apache-beam[gcp] \
                            google-cloud-bigtable google-auth urllib3

    mkdir -p /opt/pipeline

    git clone git@github.com:SunilKuruba/aws-vs-gcp-data-pipeline.git
    cd aws-vs-gcp-data-pipeline
    git checkout gcp
    cd gcp-data-pipeline

    // # ---------- 2. Push the three Python files ----------
    // cat >/opt/pipeline/publisher.py <<'PY1'
    // ${file("${path.module}/publisher.py")}
    // PY1

    // cat >/opt/pipeline/beam_processing.py <<'PY2'
    // ${file("${path.module}/beam_processing.py")}
    // PY2

    // cat >/opt/pipeline/tokenprovider.py <<'PY3'
    // ${file("${path.module}/tokenprovider.py")}
    // PY3

    // # ---------- 3. Launch both programs ----------
    // nohup /opt/venv/bin/python /opt/pipeline/publisher.py \
    //     --bootstrap-servers=${BOOTSTRAP} \
    //     --topic-name=${TOPIC} \
    //     --num_messages=100 \
    //     --delay=0.2 \
    //     >/var/log/publisher.log 2>&1 &

    // nohup /opt/venv/bin/python /opt/pipeline/beam_processing.py \
    //     >/var/log/beam.log 2>&1 &
    // EOF
}

