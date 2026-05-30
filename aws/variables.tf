variable "infra_public_key" {
  type = string
}

variable "allowed_ssh_cidr" {
    description = "CIDR allowed to SSH into EC2"
    type        = string
  
}