"""
eda.py — Exploratory Data Analysis
Run this script to generate all EDA insights and plots.
Outputs saved to data/eda_outputs/
"""
import os
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = "./data/eda_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="darkgrid", palette="muted")
plt.rcParams.update({"figure.facecolor": "#0d1117", "axes.facecolor": "#111827",
                     "text.color": "white", "axes.labelcolor": "white",
                     "xtick.color": "white", "ytick.color": "white"})

print("Loading data...")
DATA_DIR = os.getenv("DATA_DIR", "./data")
df = pd.read_csv(os.path.join(DATA_DIR, "application_train.csv"))
print(f"Shape: {df.shape}")

# ── 1. Dataset Summary ───────────────────────────────────────────────────────
print("\n=== DATASET SUMMARY ===")
print(f"Rows         : {len(df):,}")
print(f"Columns      : {df.shape[1]}")
print(f"Default rate : {df['TARGET'].mean()*100:.2f}%")
print(f"Memory usage : {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# ── 2. Data Quality ──────────────────────────────────────────────────────────
null_pct = df.isnull().mean().sort_values(ascending=False)
high_null = null_pct[null_pct > 0.3]
print(f"\nColumns with >30% nulls: {len(high_null)}")

# ── 3. Target Distribution ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4))
target_counts = df["TARGET"].value_counts()
bars = ax.bar(["Repaid (0)", "Defaulted (1)"], target_counts.values,
              color=["#3b82f6", "#ef4444"])
ax.set_title("Loan Repayment Status", color="white", fontsize=14, pad=15)
ax.set_ylabel("Count", color="white")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
            f"{bar.get_height():,}", ha="center", color="white", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "01_target_distribution.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 01_target_distribution.png")

# ── 4. Age Distribution ──────────────────────────────────────────────────────
df["age_years"] = (-df["DAYS_BIRTH"]) / 365
fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(df[df["TARGET"]==0]["age_years"], bins=40, alpha=0.6, color="#3b82f6", label="Repaid")
ax.hist(df[df["TARGET"]==1]["age_years"], bins=40, alpha=0.6, color="#ef4444", label="Defaulted")
ax.set_title("Age Distribution by Default Status", color="white", fontsize=13)
ax.set_xlabel("Age (years)")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "02_age_distribution.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 02_age_distribution.png")

# ── 5. Income Distribution ───────────────────────────────────────────────────
cap = df["AMT_INCOME_TOTAL"].quantile(0.99)
income_cap = df[df["AMT_INCOME_TOTAL"] < cap]
fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(income_cap[income_cap["TARGET"]==0]["AMT_INCOME_TOTAL"], bins=50, alpha=0.6,
        color="#3b82f6", label="Repaid")
ax.hist(income_cap[income_cap["TARGET"]==1]["AMT_INCOME_TOTAL"], bins=50, alpha=0.6,
        color="#ef4444", label="Defaulted")
ax.set_title("Income Distribution by Default Status", color="white", fontsize=13)
ax.set_xlabel("Annual Income")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "03_income_distribution.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 03_income_distribution.png")

# ── 6. Default Rate by Education ─────────────────────────────────────────────
ed_default = df.groupby("NAME_EDUCATION_TYPE")["TARGET"].mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.barh(ed_default.index, ed_default.values,
               color=plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(ed_default))))
ax.set_xlabel("Default Rate (%)")
ax.set_title("Default Rate by Education Level", color="white", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "04_default_by_education.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 04_default_by_education.png")

# ── 7. Default Rate by Income Type ───────────────────────────────────────────
inc_default = df.groupby("NAME_INCOME_TYPE")["TARGET"].mean().sort_values(ascending=False) * 100
fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(inc_default.index, inc_default.values,
       color=plt.cm.RdYlGn_r(np.linspace(0.1, 0.9, len(inc_default))))
ax.set_ylabel("Default Rate (%)")
ax.set_title("Default Rate by Income Type", color="white", fontsize=13)
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "05_default_by_income_type.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 05_default_by_income_type.png")

# ── 8. Correlation Heatmap ───────────────────────────────────────────────────
num_feats = ["TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
             "DAYS_BIRTH", "DAYS_EMPLOYED", "CNT_CHILDREN", "CNT_FAM_MEMBERS"]
corr = df[num_feats].corr()
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax,
            linewidths=0.5, cbar_kws={"shrink": 0.8})
ax.set_title("Feature Correlation Matrix", color="white", fontsize=13, pad=15)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "06_correlation_heatmap.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 06_correlation_heatmap.png")

# ── 9. Null Values Bar Chart ─────────────────────────────────────────────────
top_null = null_pct.head(20)
fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_null.index, top_null.values * 100, color="#6366f1")
ax.set_xlabel("Missing Values (%)")
ax.set_title("Top 20 Columns by Missing Data", color="white", fontsize=13)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "07_missing_values.png"), dpi=120, bbox_inches="tight")
plt.close()
print("Saved: 07_missing_values.png")

print("\n✅ EDA complete. Plots saved to", OUTPUT_DIR)

# ── Print 5 Key Business Insights ────────────────────────────────────────────
print("\n====== 5 KEY BUSINESS INSIGHTS ======")
insights = [
    f"1. Default Rate: Only {df['TARGET'].mean()*100:.1f}% of applicants defaulted — severe class imbalance requires SMOTE or class weighting.",
    f"2. Age Risk: Youngest applicants (20–30 yrs) default most; applicants aged 50+ have the lowest default rates.",
    f"3. Income Signal: Median income of defaulters (₹{df[df['TARGET']==1]['AMT_INCOME_TOTAL'].median():,.0f}) "
    f"is lower than non-defaulters (₹{df[df['TARGET']==0]['AMT_INCOME_TOTAL'].median():,.0f}).",
    f"4. Education: Lower-secondary educated applicants default at {df[df['NAME_EDUCATION_TYPE']=='Lower secondary']['TARGET'].mean()*100:.1f}% "
    f"vs {df[df['NAME_EDUCATION_TYPE']=='Higher education']['TARGET'].mean()*100:.1f}% for higher-educated.",
    f"5. Income Type: {df.groupby('NAME_INCOME_TYPE')['TARGET'].mean().idxmax()} applicants "
    f"have the highest default rate at {df.groupby('NAME_INCOME_TYPE')['TARGET'].mean().max()*100:.1f}%.",
]
for ins in insights:
    print(ins)
