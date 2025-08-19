import re
import time
import random
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://realpython.github.io/fake-jobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; JobScraperBot/1.0; +https://example.org/bot)"
}

# Canonical skill map: regex pattern -> canonical skill name
SKILL_MAP = {
    r"\bpython\b": "Python",
    r"\bsql\b": "SQL",
    r"\bexcel\b": "Excel",
    r"\b(power\s*bi|powerbi)\b": "Power BI",
    r"\btableau\b": "Tableau",
    r"\br\b": "R",
    r"\bjava\b": "Java",
    r"\bjavascript\b": "JavaScript",
    r"\btypescript\b": "TypeScript",
    r"\bhtml\b": "HTML",
    r"\bcss\b": "CSS",
    r"\breact\b": "React",
    r"\bangular\b": "Angular",
    r"\bvue\b": "Vue",
    r"\bnode(\.js)?\b": "Node.js",
    r"\bdjango\b": "Django",
    r"\bflask\b": "Flask",
    r"\bspring\b": "Spring",
    r"\baws\b": "AWS",
    r"\bazure\b": "Azure",
    r"\bgcp\b": "GCP",
    r"\bdocker\b": "Docker",
    r"\bkubernetes\b": "Kubernetes",
    r"\bgit\b": "Git",
    r"\blinux\b": "Linux",
    r"\bpandas\b": "Pandas",
    r"\bnumpy\b": "NumPy",
    r"\b(scikit-?learn|sklearn)\b": "Scikit-learn",
    r"\btensorflow\b": "TensorFlow",
    r"\bpytorch\b": "PyTorch",
    r"\b(c\+\+)\b": "C++",
    r"\bc#\b": "C#",
    r"\bc\b": "C",
    r"\bphp\b": "PHP",
    r"\bruby\b": "Ruby",
    r"\bgo(lang)?\b": "Go",
    r"\bswift\b": "Swift",
    r"\bkotlin\b": "Kotlin",
    r"\bspark\b": "Spark",
    r"\bhadoop\b": "Hadoop",
}

def extract_skills_from_text(text: str):
    """Return a sorted list of canonical skills mentioned in the text."""
    if not text:
        return []
    skills = set()
    lower = text.lower()
    for pattern, canonical in SKILL_MAP.items():
        if re.search(pattern, lower):
            skills.add(canonical)
    return sorted(skills)

def fetch_html(url: str) -> str:
    """Fetch URL and return HTML text with basic retry/backoff."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            return resp.text
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + random.random() * 2)
    return ""

def parse_jobs(html: str):
    """Parse the Fake Jobs page and return a list of job dicts."""
    soup = BeautifulSoup(html, "lxml")
    jobs = []
    for card in soup.select("div.card-content"):
        title_el = card.select_one("h2.title")
        company_el = card.select_one("h3.subtitle")
        location_el = card.select_one("p.location")
        time_el = card.select_one("time")

        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = location_el.get_text(strip=True) if location_el else ""
        posted_date = ""
        if time_el:
            posted_date = time_el.get("datetime") or time_el.get_text(strip=True)

        skills = extract_skills_from_text(title)

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "posted_date": posted_date,
                "skills": ", ".join(skills),
            }
        )
    return jobs

def main():
    print("Fetching Fake Jobs page...")
    html = fetch_html(BASE_URL)
    jobs = parse_jobs(html)
    df = pd.DataFrame(jobs)
    # Basic cleaning
    df["city"] = df["location"].str.split(",").str[0].str.strip()
    df = df.drop_duplicates()
    out = Path("jobs.csv")
    df.to_csv(out, index=False)
    print(f"Saved {len(df)} jobs to {out.resolve()}")

if __name__ == "__main__":
    main()
