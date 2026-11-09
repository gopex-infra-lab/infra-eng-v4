provider "proxmox" {
  endpoint  = replace(var.pm_api_url, "/api2/json", "")
  api_token = "${var.pm_api_token_id}=${var.pm_api_token_secret}"
  insecure  = true

  ssh {
    agent       = false
    username    = "root"
    private_key = chomp(var.infra_private_key)

    node {
      name    = "pve1"
      address = "192.168.0.253"
    }
    node {
      name    = "pve2"
      address = "192.168.0.251"
    }
    node {
      name    = "pve3"
      address = "192.168.0.254"
    }
  }
}
