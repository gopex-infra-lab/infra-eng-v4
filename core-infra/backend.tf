terraform {
  backend "local" {
    path = "/mnt/pve/nas/terraform-state/proxmox-core-v3.tfstate"
  }
}