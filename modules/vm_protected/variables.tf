variable "vm_name" {
  description = "Name of the virtual machine"
  type        = string
}
variable "target_node" {
  description = "Proxmox node where the VM will be deployed"
  type        = string
}
variable "template_name" {
  description = "Name of the cloud-init template to clone"
  type        = string
}
variable "cpu_cores" {
  description = "Number of CPU cores"
  type        = number
  default     = 1
  validation {
    condition     = var.cpu_cores >= 1 && var.cpu_cores <= 32
    error_message = "CPU cores must be between 1 and 32."
  }
}
variable "memory_mb" {
  description = "Memory size in MB"
  type        = number
  default     = 1024
  validation {
    condition     = var.memory_mb >= 512
    error_message = "Memory must be at least 512 MB."
  }
}
variable "enable_agent" {
  description = "Enable QEMU guest agent"
  type        = bool
  default     = true
}
variable "os_type" {
  description = "OS to be used"
  type        = string
  default     = "cloud-init"
}
variable "ipconfig0" {
  description = "Configure Networking"
  type        = string
  default     = "ip=dhcp"
}
variable "cicustom" {
  description = "To use files from snippets"
  type        = string
  default     = "user=local:snippets/docker-init.yml"
}
variable "full_clone" {
  type    = bool
  default = false
}

variable "target_node_ip" {
  description = "IP address of the Proxmox node for SSH connection"
  type        = string
}

variable "infra_public_key" {
  type      = string
  sensitive = true
}

variable "git_private_key" {
  type      = string
  sensitive = true
  default   = null
}

variable "infra_private_key" {
  description = "Private key for SSH to Proxmox nodes"
  type        = string
  sensitive   = true
}