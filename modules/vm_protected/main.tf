locals {
  ip_cidr = regex("ip=([^,]+)", var.ipconfig0)[0]
  ip_gw   = try(regex("gw=([^,]+)", var.ipconfig0)[0], null)
}

resource "local_file" "cloud_init" {
  filename = "${path.module}/generated/${var.vm_name}.yml"

  content = templatefile("${path.module}/cloud-init.tftpl", {
    hostname         = var.vm_name
    infra_public_key = var.infra_public_key
    git_private_key  = var.git_private_key
  })
}

resource "null_resource" "upload_snippet" {
  depends_on = [local_file.cloud_init]

  triggers = {
    cloud_init_hash = sha1(local_file.cloud_init.content)
  }

  connection {
    type        = "ssh"
    user        = "root"
    host        = var.target_node_ip
    private_key = chomp(var.infra_private_key)

    timeout = "30s"
  }

  provisioner "file" {
    source      = local_file.cloud_init.filename
    destination = "/var/lib/vz/snippets/${var.vm_name}.yml"
  }
}

resource "proxmox_virtual_environment_vm" "core" {
  name      = var.vm_name
  node_name = var.target_node
  vm_id     = var.vm_id

  on_boot             = var.onboot
  started             = var.started
  machine             = var.machine
  scsi_hardware       = "lsi"
  boot_order          = ["scsi0"]
  hotplug             = "network,disk,usb,cpu,memory"
  tablet_device       = true
  reboot_after_update  = var.reboot_after_update

  agent {
    enabled = true
  }

  cpu {
    type    = "host"
    cores   = var.cpu_cores
    sockets = 1
    numa    = true
  }

  memory {
    dedicated = var.memory_mb
  }

  network_device {
    bridge      = "vmbr0"
    model       = "virtio"
    firewall    = true
    mac_address = var.mac_address
  }

  operating_system {
    type = "l26"
  }

  initialization {
    user_data_file_id = "local:snippets/${var.vm_name}.yml"

    dns {
      servers = ["192.168.0.252"]
    }

    ip_config {
      ipv4 {
        address = local.ip_cidr
        gateway = local.ip_gw
      }
    }
  }

  clone {
    vm_id = var.template_vm_id
    full  = var.full_clone
  }

  depends_on = [null_resource.upload_snippet]

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [disk, clone, initialization, cdrom, serial_device]
  }
}
