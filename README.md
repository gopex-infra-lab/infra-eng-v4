![Terraform CI](https://github.com/gomiguel82/infra-eng-lab/actions/workflows/terraform.yml/badge.svg)

# Proxmox Infrastructure as Code Lab

## Overview

This project demonstrates Infrastructure-as-Code (IaC) provisioning of virtual machines on a Proxmox cluster using Terraform.

It simulates cloud-style infrastructure lifecycle management by defining compute resources declaratively and enabling reproducible VM deployments through code.

The goal is to model production-oriented infrastructure workflows in a controlled home lab environment.

---

## Architecture

### Proxmox

Proxmox VE serves as the virtualization platform. Terraform interacts with Proxmox using the `telmate/proxmox` provider to provision and manage virtual machines programmatically.

The Proxmox cluster acts as a private-cloud equivalent for infrastructure experimentation.

---

### Terraform State

This project uses the default local backend for Terraform state management.

State files are excluded from version control via `.gitignore` to prevent accidental exposure of environment-specific or sensitive data.

In team environments, remote backends (e.g., S3, Consul, etc.) would typically be used for shared state management and locking.

---

### VM Module

Virtual machines are defined using a reusable Terraform module located under:

modules/vm/

The module abstracts:

- CPU configuration
- Memory allocation
- Disk settings
- Network bridge configuration
- Cloud-init parameters
- SSH key injection

This modular structure follows production-grade Terraform design patterns by separating reusable infrastructure components from root configuration.

---

### Cloud-init

Cloud-init is used to initialize virtual machines at provisioning time.

It enables:

- Automated user creation
- SSH key-based authentication
- Initial configuration without manual intervention

This mimics how cloud providers (AWS, Azure, GCP) bootstrap instances.

---

### Variables

Infrastructure configuration is parameterized using input variables.

Examples include:

- VM name
- CPU count
- Memory size
- Disk size
- Network configuration
- SSH public key

Sensitive or environment-specific values are excluded from version control and defined via:

terraform.tfvars (local only)

This ensures reproducibility while maintaining security hygiene.

---

## Usage

Initialize Terraform:
```text
terraform init
```
Apply infrastructure changes:
```text
terraform apply
```
Destroy provisioned resources:
```text
terraform destroy
```
---
## Repository Structure
```text
.
├── locals.tf
├── main.tf
├── variables.tf
├── outputs.tf
├── provider.tf
├── versions.tf
├── modules/
│   └── vm/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── versions.tf
└── .github/
    └── workflows/
        └── terraform.yml
```

## CI / Validation

A GitHub Actions workflow validates Terraform configuration on push and pull requests by running:

- `terraform init`
- `terraform fmt -check`
- `terraform validate`

This simulates a basic CI pipeline commonly used in production environments.

---

## Why This Matters

This project demonstrates Infrastructure-as-Code provisioning of virtual machines using Terraform and the Proxmox provider, simulating cloud-style reproducible environments. It reflects production engineering practices such as modular design, parameterization, lifecycle management, and automated validation workflows.
