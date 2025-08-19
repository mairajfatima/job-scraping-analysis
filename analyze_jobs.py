from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

data_path = Path("jobs.csv")
if not data_path.exists():
    raise SystemExit("jobs.csv not found. Run `python scrape_jobs.py` first.")

df = pd.read_csv(data_path)

# Split the skills column into lists
df["skills_list"] = df["skills"].fillna("").apply(
    lambda s: [x.strip() for x in s.split(",") if x.strip()]
)

# Explode for counting
exploded = df.explode("skills_list")

# Overall top skills
skill_counts = exploded["skills_list"].value_counts().head(20)

Path("plots").mkdir(exist_ok=True)

# Chart 1: Top skills overall (from titles)
plt.figure()
skill_counts.iloc[::-1].plot(kind="barh")  # reverse for nicer order
plt.title("Top Skills in Job Titles")
plt.xlabel("Count")
plt.tight_layout()
plt.savefig("plots/top_skills_overall.png", dpi=160)
plt.close()

# Bonus: Visualize most frequent skills by city
top_cities = df["city"].value_counts().head(5).index.tolist()
for city in top_cities:
    subset = exploded[exploded["city"] == city]
    counts = subset["skills_list"].value_counts().head(10)
    if counts.empty:
        continue
    plt.figure()
    counts.iloc[::-1].plot(kind="barh")
    plt.title(f"Top Skills in Titles — {city}")
    plt.xlabel("Count")
    plt.tight_layout()
    safe_city = "".join(c for c in city if c.isalnum() or c in (" ", "-", "_")).strip().replace(" ", "_")
    plt.savefig(f"plots/skills_by_city_{safe_city}.png", dpi=160)
    plt.close()

# Save a pivot table for reference
pivot = (
    exploded[exploded["city"].isin(top_cities)]
    .pivot_table(index="city", columns="skills_list", aggfunc="size", fill_value=0)
    .sort_index()
)
pivot.to_csv("skills_by_city.csv")

print("Done! See plots/ and skills_by_city.csv.")
