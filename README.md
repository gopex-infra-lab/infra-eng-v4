# Infrastructure Automation Lab (Proxmox + Terraform + Ansible + Docker)

Production-style infrastructure automation lab demonstrating Terraform, Ansible, Docker, and CI/CD workflows in a Proxmox-based environment.

[![Deploy (Terraform + Ansible)](https://github.com/gopex-infra-lab/infra-eng-v4/actions/workflows/deploy.yml/badge.svg)](https://github.com/gopex-infra-lab/infra-eng-v4/actions/workflows/deploy.yml)

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
```
Terraform → Proxmox VM → Cloud-init → Ansible → Docker → Application (FastAPI + PostgreSQL + Nginx) + Monitoring (Prometheus + Grafana)
```
---

## Database Persistence & Backup

The FastAPI application uses PostgreSQL as a stateful service, deployed via Docker Compose.

### Persistence Model

- PostgreSQL data is stored in a named Docker volume (`fastapi_postgres_data`)
- Data persists across container restarts and recreations
- Volume is managed by Docker and mounted at `/var/lib/postgresql/data`

This ensures application state is retained independently of container lifecycle.

### Backup

Manual backup can be performed using:

```bash
docker exec postgres_lab pg_dump -U <user> <db> > /opt/backups/postgres/backup.sql
```
Restoring backup can be done using:
```bash
cat /opt/backups/postgres/backup.sql | docker exec -i postgres_lab psql -U $POSTGRES_USER $POSTGRES_DB
```

## Reverse Proxy

The FastAPI application is exposed via an Nginx reverse proxy.

- Nginx listens on port 80
- Routes traffic to the FastAPI container (internal network)
- Application container is not exposed directly

## Monitoring

The stack includes a full observability layer deployed via Docker Compose:

- **Prometheus** — scrapes metrics from node-exporter and cAdvisor
- **Grafana** — dashboards provisioned via config files (no manual setup)
- **node-exporter** — host-level metrics (CPU, memory, disk, network)
- **cAdvisor** — per-container resource usage metrics

All services run on the internal `app_net` network and are not directly exposed.

## Repository Structure
```text
.
├── ansible/        # Configuration management (roles, playbooks)
├── cloud-init/     # VM initialization templates
├── docker/         # Application deployment (docker-compose)
│   ├── fastapi/    # App + Nginx + Prometheus + Grafana
│   └── monitoring/ # Prometheus and Grafana config
├── lab/            # Application infrastructure environment
├── core-infra/     # Shared infrastructure (base services)
├── modules/        # Reusable Terraform modules
├── app/            # Sample FastAPI application
└── .github/        # CI workflows (Terraform validation)
```
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
```bash
cd lab
terraform init
terraform apply
```
Post-provisioning (configuration + app deployment):
```bash
ansible-playbook -i inventory site.yml
```
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

## Prerequisites

- Proxmox VE node with API token and a cloud-init-ready VM template
- Terraform >= 1.5
- Ansible >= 2.14 with `community.docker` collection
- GitHub Actions self-hosted runner registered to the repo
- SSH key pair for infrastructure access

## CI / CD 

All provisioning runs through GitHub Actions — there is no local Terraform or Ansible execution required.

1. Trigger the **Deploy** workflow manually via `workflow_dispatch`, selecting environment (`lab`, `core`, `aws`) and action (`plan`, `apply`, `destroy`)
2. Terraform provisions VMs on Proxmox (or EC2 for `aws`) and generates the Ansible inventory automatically
3. Ansible configures the VMs and deploys the Docker stack

Required GitHub Actions secrets are listed in `.tfvars.example`.

### aws

* Cloud environment provisioning an EC2 instance on AWS
* Uses the same Ansible roles as lab for application deployment