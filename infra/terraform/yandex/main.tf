provider "yandex" {
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = var.zone
}

resource "yandex_vpc_network" "platform" {
  name = "${var.project}-network"
}

resource "yandex_vpc_subnet" "platform" {
  name           = "${var.project}-subnet"
  zone           = var.zone
  network_id     = yandex_vpc_network.platform.id
  v4_cidr_blocks = ["10.10.0.0/24"]
}

resource "yandex_storage_bucket" "lakehouse" {
  bucket     = "${var.project}-lakehouse"
  access_key = yandex_iam_service_account_static_access_key.s3.access_key
  secret_key = yandex_iam_service_account_static_access_key.s3.secret_key
  acl        = "private"
  versioning { enabled = true }
  lifecycle_rule {
    id      = "raw-retention"
    enabled = true
    prefix  = "bronze/"
    expiration { days = 365 }
  }
}

resource "yandex_iam_service_account_static_access_key" "s3" {
  service_account_id = var.service_account_id
  description        = "Static key for S3-compatible Object Storage lakehouse bucket"
}

resource "yandex_mdb_kafka_cluster" "streaming" {
  name        = "${var.project}-kafka"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.platform.id
  subnet_ids  = [yandex_vpc_subnet.platform.id]

  config {
    version          = "3.6"
    brokers_count    = 1
    zones            = [var.zone]
    assign_public_ip = false
    schema_registry  = false
      kafka {
        resources {
          resource_preset_id = "s2.micro"
          disk_type_id       = "network-ssd"
          disk_size          = 16
      }
    }
  }

  user {
    name     = "platform"
    password = var.kafka_user_password
    permission {
      topic_name = "*"
      role       = "ACCESS_ROLE_PRODUCER"
    }
    permission {
      topic_name = "*"
      role       = "ACCESS_ROLE_CONSUMER"
    }
  }
}

resource "yandex_compute_instance" "airflow_vm" {
  name        = "${var.project}-airflow-vm"
  platform_id = "standard-v3"
  zone        = var.zone

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = var.vm_image_id
      size     = 40
      type     = "network-ssd"
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.platform.id
    nat       = true
  }

  metadata = {
    ssh-keys  = "ubuntu:${var.ssh_public_key}"
    user-data = templatefile("${path.module}/cloud-init-airflow.yaml.tftpl", {
      s3_bucket          = yandex_storage_bucket.lakehouse.bucket
      s3_access_key      = yandex_iam_service_account_static_access_key.s3.access_key
      s3_secret_key      = yandex_iam_service_account_static_access_key.s3.secret_key
      kafka_bootstrap    = yandex_mdb_kafka_cluster.streaming.host[0].name
          project_repository = "git@gitlab.local:coworkbooking/data-platform.git"
    })
  }
}
