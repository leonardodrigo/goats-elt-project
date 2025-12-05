terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}
resource "docker_image" "kafka" {
  name = "apache/kafka:latest"
}

# Broker service
resource "docker_container" "broker" {
  name  = "elt-broker"
  image = docker_image.kafka.image_id

  hostname = "elt-broker"

  ports {
    internal = 9092
    external = 9092
  }

  env = [
    "KAFKA_BROKER_ID=1",
    "KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT,CONTROLLER:PLAINTEXT",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092",
    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1",
    "KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS=0",
    "KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1",
    "KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1",
    "KAFKA_PROCESS_ROLES=broker,controller",
    "KAFKA_NODE_ID=1",
    "KAFKA_CONTROLLER_QUORUM_VOTERS=1@broker:29093",
    "KAFKA_LISTENERS=PLAINTEXT://broker:29092,CONTROLLER://broker:29093,PLAINTEXT_HOST://0.0.0.0:9092",
    "KAFKA_INTER_BROKER_LISTENER_NAME=PLAINTEXT",
    "KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER",
    "KAFKA_LOG_DIRS=/tmp/kraft-combined-logs",
    "CLUSTER_ID=MkU3OEVBNTcwNTJENDM2Qk",
  ]

  networks_advanced {
    name    = var.network_name
    aliases = ["broker"]
  }
}

# Kafka topic initialization
resource "docker_container" "kafka_init" {
  name  = "kafka-init"
  image = docker_image.kafka.image_id

  depends_on = [docker_container.broker]

  networks_advanced {
    name = var.network_name
  }

  entrypoint = ["bash", "-c"]

  command = [
    <<-EOT
    echo "Creating topic...";
    /opt/kafka/bin/kafka-topics.sh --create \
      --bootstrap-server broker:29092 \
      --topic spotify-streaming \
      --partitions 3 \
      --replication-factor 1 \
      || echo "Topic already exists...";
    EOT
  ]

  must_run = false # allow container to exit after command
}


# Kafka UI
resource "docker_image" "kafka_ui" {
  name = "provectuslabs/kafka-ui:latest"
}

resource "docker_container" "kafka_ui" {
  name  = "kafka-ui"
  image = docker_image.kafka_ui.image_id

  depends_on = [
    docker_container.broker,
    docker_container.kafka_init,
  ]

  ports {
    internal = 8080
    external = 8082
  }

  env = [
    "DYNAMIC_CONFIG_ENABLED=true",
    # plus your KAFKA_UI configuration pointing at broker:29092 on elt_internal
  ]

  networks_advanced {
    name = var.network_name
  }
}
