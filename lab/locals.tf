locals {
  defaults = yamldecode(file("${path.module}/vm_defaults.yaml"))

  vm_files = fileset("${path.module}/vms", "*.yaml")

  vm_list = [
    for f in local.vm_files :
    yamldecode(file("${path.module}/vms/${f}"))
  ]

  vm_config = {
    for vm in local.vm_list :
    vm.vm_name => merge(local.defaults, vm)
  }
}