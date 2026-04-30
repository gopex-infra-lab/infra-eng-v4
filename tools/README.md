# Job Scraper (DevOps Automation Pipeline)

Automated system that discovers, ranks, and tracks DevOps, SRE, Platform, and Senior SysAdmin roles based on infrastructure and automation signals.

---

## Features

- Job discovery via SerpAPI (Google Jobs)
- Intelligent scoring engine (Terraform, Kubernetes, Cloud, Ansible)
- Context-aware filtering (removes low-signal / irrelevant roles)
- Deduplication via SQLite (no repeated jobs)
- Daily execution via GitHub Actions
- Email digest with prioritized results (HIGH / MEDIUM)
- REST API (FastAPI) to browse stored jobs

---

## Architecture

GitHub Actions (scheduled)
→ Python scraper
→ Scoring engine
→ SQLite database (jobs.db)
→ Email notification

Optional:
→ FastAPI service to expose stored results

---

## Stack

Python • SQLite • GitHub Actions • Docker • FastAPI

---

## Purpose

This project demonstrates:

- Automated data pipelines
- API integration (SerpAPI)
- Intelligent filtering and ranking systems
- Persistent state management (SQLite)
- CI/CD scheduling (GitHub Actions)
- Containerized batch workloads

---

## Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export SERPAPI_KEY=...
export EMAIL_FROM=...
export EMAIL_TO=...
export EMAIL_PASSWORD=...

python scraper.py