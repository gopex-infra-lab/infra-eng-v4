import {
  for_each = local.vm_config
  to       = module.core[each.key].proxmox_virtual_environment_vm.core
  id       = "${each.value.target_node}/${each.value.vm_id}"
}
