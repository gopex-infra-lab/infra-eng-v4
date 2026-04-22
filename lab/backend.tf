terraform {
  backend "local" {
    path = "/mnt/pve/nas/terraform-state/proxmox-lab-v3.tfstate"
  }
}