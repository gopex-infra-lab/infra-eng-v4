module "lab_vm" {
  source = "../modules/vm"

  for_each = local.vm_config

  vm_name        = each.value.vm_name
  target_node    = each.value.target_node
  target_node_ip = each.value.target_node_ip

  cpu_cores = each.value.cpu_cores
  memory_mb = each.value.memory_mb
  ipconfig0 = each.value.ipconfig0

  template_name = each.value.template_name
  full_clone    = each.value.full_clone

  # keep your current keys
  infra_public_key  = var.infra_public_key
  infra_private_key = var.infra_private_key
  git_private_key   = var.git_private_key
}

resource "local_file" "ansible_inventory" {
  filename = "${path.module}/../ansible/inventory/lab.ini"

  content = <<EOT
[fastapi]
%{for vm_name, vm in local.vm_config~}
%{if vm.role == "fastapi"}
${vm_name} ansible_host=${vm.ip} ansible_user=gomg
%{endif}
%{endfor}

[simmbus]
%{for vm_name, vm in local.vm_config~}
%{if vm.role == "all"}
${vm_name} ansible_host=${vm.ip} ansible_user=gomg
%{endif}
%{endfor}
EOT
}