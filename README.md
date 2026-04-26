# Infrastructure Automation Lab (Proxmox + Terraform + Ansible + Docker)

## Overview

This project demonstrates Infrastructure-as-Code (IaC) and system automation by provisioning and managing virtual machines on a Proxmox cluster.

It simulates production-style infrastructure workflows including:

* VM provisioning using Terraform
* System initialization using cloud-init
* Configuration management using Ansible
* Application deployment using Docker
* CI validation using GitHub Actions

The objective is to model real-world infrastructure operations in a controlled environment.

---

## Architecture

Terraform provisions virtual machines on Proxmox, which are initialized using cloud-init.
Post-provisioning configuration is handled by Ansible, and applications are deployed using Docker.

Flow:

Terraform → Proxmox VM → Cloud-init → Ansible → Docker → Application (FastAPI + PostgreSQL)

---

## Repository Structure

.
├── ansible/        # Configuration management (roles, playbooks)
├── cloud-init/     # VM initialization templates
├── docker/         # Application deployment (docker-compose)
├── lab/            # Application infrastructure environment
├── core-infra/     # Shared infrastructure (base services)
├── modules/        # Reusable Terraform modules
├── app/            # Sample FastAPI application
└── .github/        # CI workflows (Terraform validation)

---

## Environments

### lab

* Application-focused environment
* Deploys virtual machines running containerized services

### core-infra

* Shared infrastructure layer
* Intended for foundational services (DNS, utilities, etc.)

---

## Key Features

* Infrastructure provisioning using Terraform and Proxmox API
* Modular Terraform design (reusable VM modules)
* Automated VM initialization using cloud-init
* Configuration management using Ansible roles
* Containerized application deployment using Docker Compose
* CI pipeline for Terraform validation (GitHub Actions)
* Multi-environment separation (lab vs core-infra)

---

## Example Workflow

Provision infrastructure:

cd lab
terraform init
terraform apply

Post-provisioning (configuration + app deployment):

ansible-playbook -i inventory site.yml

---

## CI / Validation

GitHub Actions workflow validates infrastructure code on each push:

* terraform fmt
* terraform validate

This ensures consistency and correctness of infrastructure definitions.

---

## Technologies Used

* Terraform
* Proxmox (KVM)
* Ansible
* Docker / Docker Compose
* GitHub Actions
* Linux

---

## Purpose

This project is designed to:

* Simulate real-world infrastructure provisioning and management
* Practice DevOps workflows (IaC, CI/CD, automation)
* Build and troubleshoot production-like environments
* Improve system administration and infrastructure engineering skills

---

## Notes

* Sensitive data (credentials, tokens, keys) are not stored in the repository
* Environment-specific values are managed outside version control
