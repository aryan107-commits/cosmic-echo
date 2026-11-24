import pandas as pd
import matplotlib.pyplot as plt

file_path = "data/processed/source_candidates.csv"

df = pd.read_csv(file_path)

print("Total candidates:", len(df))
print("\nCandidate statistics:")
print(df[["flux_mjy_sr", "variance", "snr"]].describe())

plt.figure(figsize=(10, 6))
plt.hist(df["snr"], bins=100)
plt.xlabel("Preliminary significance proxy")
plt.ylabel("Number of candidates")
plt.title("COSMIC ECHO — Candidate Distribution")
plt.yscale("log")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("data/processed/candidate_distribution.png", dpi=200)
plt.show()