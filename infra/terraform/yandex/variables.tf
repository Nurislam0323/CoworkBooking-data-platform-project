variable "cloud_id" { type = string }
variable "folder_id" { type = string }
variable "zone" { type = string default = "ru-central1-a" }
variable "project" { type = string default = "coworkbooking-data-platform" }
variable "ssh_public_key" { type = string }
variable "vm_image_id" { type = string default = "fd8vmcue7aajpmeo39kk" }
variable "service_account_id" { type = string }
variable "kafka_user_password" { type = string sensitive = true }
