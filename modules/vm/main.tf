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

resource "proxmox_vm_qemu" "lab_vm" {
  name        = var.vm_name
  target_node = var.target_node
  clone       = var.template_name

  cores  = var.cpu_cores
  memory = var.memory_mb
  network {
    model    = "virtio"
    bridge   = "vmbr0"
    firewall = true
  }

  ipconfig0  = var.ipconfig0
  nameserver = "192.168.0.252"
  agent      = 1

  cicustom   = "user=local:snippets/${var.vm_name}.yml"
  full_clone = var.full_clone

  depends_on = [
    null_resource.upload_snippet
  ]

  qemu_os = "l26"

  bootdisk = "scsi0"
  boot     = "order=scsi0"

  lifecycle {
    prevent_destroy = false
    ignore_changes = [
      disk
    ]
  }
}