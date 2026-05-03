import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time
import urllib.parse
import base64
from collections import defaultdict
import re
import os
from db import init_db, insert_job

DB_NAME = os.getenv("DB_PATH", "jobs.db")

# =========================
# CONFIG
# =========================
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

QUERIES = [
    "Systems Administrator Montreal",
    "DevOps Engineer Montreal",
    "SRE Montreal",
    "Platform Engineer Montreal",
    "Infrastructure Engineer Montreal"
]

# --- Cloud intensity ---
CLOUD_KEYWORDS = ["aws", "azure", "gcp", "eks", "lambda", "cloudformation"]

# --- Boost your profile ---
BOOST = {
    "terraform": 3,
    "docker": 3,
    "linux": 3,
    "ansible": 2,
    "ci": 2,
    "cd": 2,
    "network": 2,
    "application support": 2,
    "production support engineer": 2,
}

# --- Title boost ---
TITLE_BOOST = {
    "devops": 5,
    "platform engineer": 5,
    "site reliability": 5,
    "systems engineer": 4,
    "infrastructure engineer": 4,
    "system administrator": 3,
    "senior systems administrator": 4
}

KEYWORDS = {
    # Core roles (high signal)
    "devops": 4,
    "site reliability": 4,
    "sre": 4,
    "platform": 3,
    "infrastructure": 3,
    "sysadmin": 3,
    "system administrator": 3,
    
    # Infra-as-Code (priority for your transition)
    "terraform": 6,
    "ansible": 3,

    # Containers / orchestration
    "kubernetes": 5,
    "docker": 4,

    # Cloud
    "aws": 1,
    "azure": 1,
    "gcp": 1,

    # Supporting signals
    #"cloud": 2,
    "ci": 2,
    "cd": 2,
    "pipeline": 2,
    "automation": 2
}

ROLE_WEIGHTS = {
    "devops": 5,
    "sre": 5,
    "site reliability": 5,
    "platform": 4,
    "infrastructure": 4,

    "cloud": 1,

    # SysAdmin tier (intentionally lower)
    "sysadmin": 4,
    "system administrator": 4,
    "it administrator": 3,

    "application support": 3,
    "production support": 3,
    "trading support": 4,
    "support engineer": 2,
}

ROLE_TYPES = {
    "cloud_heavy": ["aws", "azure", "gcp", "eks", "lambda", "cloud"],
    "hybrid_devops": ["terraform", "ci", "cd", "docker", "ansible"],
    "platform_sre": ["sre", "site reliability", "observability", "on-call"],
    "sysadmin_modern": ["linux", "network", "infrastructure", "vmware", "proxmox"],
    "app_support": [
        "application support engineer",
        "production support engineer",
        "trading support",
        "technical support engineer",
        "systems support",
        "operations support"
    ]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive"
}
# SerpAPI
def search_serpapi(query):
    url = "https://serpapi.com/search"

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "gl": "ca",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    r = requests.get(url, params=params)
    data = r.json()

    results = []

    for job in data.get("jobs_results", []):
        title = job.get("title", "")
        # extract best available link (priority order)
        link = (
            job.get("link") or
            (job.get("apply_options") or [{}])[0].get("link", "") or
            (job.get("related_links") or [{}])[0].get("link", "") or
            ""
        )

        # extract usable link
        if "related_links" in job and job["related_links"]:
            link = job["related_links"][0].get("link", "")

        results.append({
            "title": title,
            "company": job.get("company_name", ""),
            "description": job.get("description", ""),
            "link": link
        })

    print(f"[DEBUG] SerpAPI results: {len(results)}")
    return results

# =========================
# FETCH JOB PAGE
# =========================
def fetch_job_description(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        text = soup.get_text(separator=" ").lower()
        return text
    except:
        return ""

def classify_domain(url):
    try:
        domain = url.split("/")[2]

        if "lever.co" in domain or "greenhouse.io" in domain:
            return "direct"

        if "linkedin.com" in domain or "indeed" in domain or "glassdoor" in domain:
            return "job_board"

        return "other"
    except:
        return "unknown"

# =========================
# SCORING
# =========================
def classify_role(text):
    text = text.lower()
    scores = {}

    for role, keywords in ROLE_TYPES.items():
        scores[role] = sum(1 for k in keywords if k in text)

    best_role = max(scores, key=scores.get)

    # fallback if nothing matched
    """if scores[best_role] == 0:
        return "unknown"""
    # Require minimum confidence
    if scores[best_role] < 2:
        return "unknown"

    return best_role


def cloud_score(text):
    text = text.lower()
    return sum(1 for k in CLOUD_KEYWORDS if k in text)

def score_job(text):
    score = 0
    matched = []

    text = text.lower()

    # Role scoring (primary driver)
    for role, weight in ROLE_WEIGHTS.items():
        if role in text:
            score += weight
            if role not in matched:
                matched.append(role)

    # Tech stack scoring
    for k, weight in KEYWORDS.items():
        if k in text:
            score += weight
            if k not in matched:
                matched.append(k)
    
    # --- Profile boost ---
    for k, weight in BOOST.items():
        if k in text:
            score += weight
            if k not in matched:
                matched.append(k)

    c_score = cloud_score(text)
    role_type = classify_role(text)

    # Penalize low-value support roles
    if any(x in text for x in [
        "end-user", "desktop support", "helpdesk",
        "technical support representative", "it support specialist"
    ]):
        score -= 6
        matched.append("low_value_support")

    # Penalize cloud-heavy
    score -= c_score * 1

    # Penalize niche / non-infra domains
    if any(x in text for x in [
        "gis", "sap", "crm", "erp", "salesforce"
    ]):
        score -= 4
        matched.append("domain_penalty")
    
    # Penalize generic support engineer roles
    if "support engineer" in text and not any(x in text for x in [
        "application support engineer",
        "production support engineer"
    ]):
        score -= 4
        matched.append("support_engineer_penalty")
    
    if is_senior(text):
        score -= 4
        matched.append("senior_penalty")

    score = min(score, 20)

    return score, matched, role_type, c_score

def is_senior(text):
    text = text.lower()

    return (
        any(re.search(rf"\b{x}\b", text) for x in ["senior", "staff", "principal"])
        or re.search(r"\blead(?!ing)\b", text)
    ) and not any(x in text for x in ["junior", "jr"])

def score_description(desc):
    desc = desc.lower()

    bonus = 0
    matched = []

    for k, weight in KEYWORDS.items():
        if k in desc:
            bonus += int(weight * 0.5)
            matched.append(k)

    return bonus, matched

def final_score(score, role_type, cloud_score):
    adjusted = score

    if role_type == "hybrid_devops":
        adjusted += 5
    elif role_type == "platform_sre":
        adjusted += 4
    elif role_type == "sysadmin_modern":
        adjusted += 3
    elif role_type == "app_support":
        adjusted += 2

    if role_type == "cloud_heavy":
        adjusted -= 6

    adjusted -= cloud_score * 1

    return adjusted


def classify_decision(f_score):
    if f_score >= 12:
        return "APPLY"
    elif f_score >= 7:
        return "MAYBE"
    else:
        return "SKIP"

def is_relevant(role_type, cloud_score):
    if role_type == "unknown":
        return False
    return True

# =========================
# EMAIL
# =========================
def send_email(jobs):

    grouped = defaultdict(list)

    for job in jobs:
        grouped[job["query"]].append(job)
        
    now = datetime.now().strftime("%Y-%m-%d")

    body = ""

    for query, q_jobs in grouped.items():
        body += f"\n=== {query} ({len(q_jobs)} roles) ===\n\n"

        for j in q_jobs:
            body += f"[{j['score']}] {j['title']} ({j['company']})\n"
            body += f"{j['link']}\n"
            body += f"Skills: {', '.join(j.get('matched', []))}\n\n"

    msg = MIMEText(body)
    msg["Subject"] = f"{now} - {len(jobs)} matching roles found"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

# =========================
# MAIN
# =========================
def main():
    init_db()
    seen_titles = set()
    scored_jobs = []

    query_groups = [
        ["DevOps Engineer Montreal Canada", "Junior DevOps Engineer Canada"],
        ["Application Support Engineer Montreal Canada", "Production Support Engineer Montreal Canada"],
        ["Linux System Administrator Montreal Canada", "Systems Engineer Montreal Canada"]
    ]

    day_index = datetime.now().day % len(query_groups)
    active_queries = query_groups[day_index]

    results = []

    for q in active_queries:
        print(f"[DEBUG] Using query: {q}")
        q_results = search_serpapi(q)

        for r in q_results:
            r["__query"] = q   # ← attach query to each result
            results.append(r)

    print(f"[DEBUG] Total results: {len(results)}")

    for r in results:
        title = r.get("title", "")
        company = r.get("company", "")
        description = r.get("description", "")
        raw_url = r.get("link", "")

        if raw_url and raw_url.startswith("http"):
            url = raw_url
        else:
            search_query = f"{title} {company} Canada"
            url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"

        if not title or len(title) < 5:
            continue

        combined_text = f"{title} {company} {description}".lower()

        # ==================================================
        # PHASE 1 — HARD FILTERS (NO score, NO role_type)
        # ==================================================

        # Non-IT / low-value roles
        if any(x in combined_text for x in [
            "sewing", "garment", "factory", "warehouse", "labour",
            "production line", "packing", "cleaning",
            "helpdesk", "desktop support", "end-user",
            "customer service", "call center", "technical support representative"
        ]):
            continue

        # Cloud specialists (not your target)
        if any(x in combined_text for x in [
            "cloud architect", "cloud engineer",
            "aws engineer", "azure engineer",
            "cloud platform engineer", "cloud specialist"
        ]):
            continue

        # Domain-specific (low relevance)
        if any(x in combined_text for x in [
            "salesforce", "erp", "crm"
        ]):
            continue

        # Cloud-dominant DevOps (your strict rule)
        cloud_hits = sum(x in combined_text for x in ["aws", "azure", "gcp"])

        if (
            "devops" in combined_text
            and cloud_hits >= 2
            and any(x in combined_text for x in ["cloud", "kubernetes", "platform"])
        ):
            continue

        # ==================================================
        # PHASE 2 — SCORING (safe zone)
        # ==================================================

        score, matched, role_type, c_score = score_job(combined_text)

        # define helper flag AFTER scoring
        is_sysadmin = role_type == "sysadmin_modern"

        # reject unknown roles (but allow devops signals)
        if role_type == "unknown":
            if not any(x in combined_text for x in [
                "devops", "ci/cd", "docker", "automation", "pipeline"
            ]):
                continue

        # reject senior devops only
        if "devops" in combined_text and is_senior(combined_text):
            continue

        # -------------------------
        # SCORING ADJUSTMENTS
        # -------------------------

        # infra bias (your target)
        if any(x in combined_text for x in [
            "linux", "infrastructure", "unix", "network"
        ]):
            score += 4

        # devops signals
        if any(x in combined_text for x in [
            "docker", "ci/cd", "terraform", "ansible"
        ]):
            score += 2

        # generic support penalty
        if "support engineer" in combined_text and not any(x in combined_text for x in [
            "application support engineer",
            "production support engineer"
        ]):
            score -= 4

        # senior penalty (non-sysadmin only)
        if is_senior(combined_text) and not is_sysadmin:
            score -= 4
            matched.append("senior_penalty")

        # light cloud penalty
        if cloud_hits >= 2:
            score -= 2

        # ==================================================
        # PHASE 3 — FINAL DECISION
        # ==================================================

        f_score = final_score(score, role_type, c_score)
        decision = classify_decision(f_score)

        if decision == "SKIP":
            continue

        category = decision

        # store job
        job = {
            "title": title,
            "company": company,
            "link": url,
            "score": score,
            "category": category,
            "matched": matched,
            "query": r.get("__query", "unknown")
        }

        insert_job(job)
        scored_jobs.append(job)

        time.sleep(1)

    # Sort + select
    scored_jobs.sort(key=lambda x: x["score"], reverse=True)
    final_jobs = scored_jobs[:8]

    print(f"[DEBUG] Final selected: {len(final_jobs)}")

    send_email(final_jobs)
    print("Email sent.")

if __name__ == "__main__":
    main()
