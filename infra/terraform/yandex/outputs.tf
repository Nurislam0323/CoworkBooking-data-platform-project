output "bucket_name" { value = yandex_storage_bucket.lakehouse.bucket }
output "kafka_cluster_id" { value = yandex_mdb_kafka_cluster.streaming.id }
output "airflow_vm_public_ip" { value = yandex_compute_instance.airflow_vm.network_interface[0].nat_ip_address }
output "airflow_url" { value = "http://${yandex_compute_instance.airflow_vm.network_interface[0].nat_ip_address}:8080" }
