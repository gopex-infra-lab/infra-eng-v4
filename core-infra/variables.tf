variable "pm_api_url" {
  description = "Proxmox API URL"
  type        = string
}

variable "pm_api_token_id" {
  description = "Proxmox API token ID"
  type        = string
}

variable "pm_api_token_secret" {
  description = "Proxmox API token secret"
  type        = string
  sensitive   = true
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
  type      = string
  sensitive = true
  default   = null
}