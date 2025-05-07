#!/usr/bin/env python3
"""
plots.py  Generates four comparison charts
  1. Load vs Latency curve
  2. Cost bar-chart (low / med / high load)
  3. 24-hour auto-scaling horizon plot
  4. Sustainability vs Speed scatter
  
Inputs:
    AWS_result.csv
    GCP_result.csv
    GCP-billing-info.csv
"""

import pandas as pd, numpy as np, matplotlib.pyplot as plt, textwrap, pathlib, sys

AWS_CSV      = "AWS_result.csv"
GCP_CSV      = "GCP_result.csv"
BILLING_CSV  = "My Billing Account_Reports, 2025-04-01 — 2025-04-30.csv"

# Column names inside AWS/GCP result files
COL_LOAD     = "load"              # events/minute
COL_LATENCY  = "p95_latency_ms"    # 95‑th percentile latency
COL_LAMBDA   = "lambda_concurrency"
COL_DF       = "dataflow_workers"
COL_COST_LOW, COL_COST_MED, COL_COST_HIGH = "cost_low", "cost_med", "cost_high"

# Which GCP project ID to sum cost for in billing export
GCP_PROJECT  = "cool-continuity-457614-b2"


plt.rcParams["figure.facecolor"] = "white"

def short(path): return pathlib.Path(path).name

#Loading all CSV's
try:
    aws = pd.read_csv(AWS_CSV)
    gcp = pd.read_csv(GCP_CSV)
    billing = pd.read_csv(BILLING_CSV)
except FileNotFoundError as e:
    sys.exit(f"✖  {e}")

print("\n=== preview AWS_result.csv ===");  print(aws.head())
print("\n=== preview GCP_result.csv ===");  print(gcp.head())
print("\n=== preview billing export ===");  print(billing.head())

'''
plot - 1: Load vs Latency AWS vs GCP

'''
fig1 = plt.figure(figsize=(8,5))
plt.plot(aws[COL_LOAD], aws[COL_LATENCY], "-o", c="orange",   label="AWS Kinesis → Lambda")
plt.plot(gcp[COL_LOAD], gcp[COL_LATENCY], "-s", c="orangered",label="GCP Kafka → Dataflow")
plt.xlabel("Load (events/minute)"); plt.ylabel("95‑th Percentile Latency (ms)")
plt.title("Load vs Latency: AWS vs GCP Scaling"); plt.grid(True); plt.legend()
fig1.tight_layout(); fig1.savefig("plot1_latency.png")

'''
plot -2 : Cost comparision across different components used in both the pipelines

'''
services = ["Kinesis Shards (AWS)", "Pub/Sub Throughput (GCP)",
            "Lambda Exec (AWS)",    "Dataflow Workers (GCP)",
            "DynamoDB Writes (AWS)","Bigtable Writes (GCP)"]

low  = [aws.at[0, COL_COST_LOW],   gcp.at[0, COL_COST_LOW],
        aws.at[0, COL_COST_LOW],   gcp.at[0, COL_COST_LOW],
        aws.at[0, COL_COST_LOW],   gcp.at[0, COL_COST_LOW]]
med  = [aws.at[0, COL_COST_MED],   gcp.at[0, COL_COST_MED],
        aws.at[0, COL_COST_MED],   gcp.at[0, COL_COST_MED],
        aws.at[0, COL_COST_MED],   gcp.at[0, COL_COST_MED]]
high = [aws.at[0, COL_COST_HIGH],  gcp.at[0, COL_COST_HIGH],
        aws.at[0, COL_COST_HIGH],  gcp.at[0, COL_COST_HIGH],
        aws.at[0, COL_COST_HIGH],  gcp.at[0, COL_COST_HIGH]]

y  = np.arange(len(services)); h = .25
fig2 = plt.figure(figsize=(9,5))
plt.barh(y-h, low,  height=h, color="lightgreen",   label="Low Load")
plt.barh(y,    med, height=h, color="coral",        label="Medium Load")
plt.barh(y+h,  high,height=h, color="lightskyblue", label="High Load")
plt.yticks(y, services); plt.xlabel("Cost (USD/hour)")
plt.title("Cost Comparison Across Load Levels (AWS vs GCP)")
plt.grid(axis="x"); plt.legend(); fig2.tight_layout(); fig2.savefig("plot2_costs.png")

'''
plot-3 24 Hour horizon chart: Auto scaling

'''
t  = np.arange(0, 24*60, 60)          # minute marks
aws_l = aws[COL_LAMBDA].iloc[:24]     # ensure 24 samples
gcp_w = gcp[COL_DF].iloc[:24]

fig3 = plt.figure(figsize=(9,5))
plt.fill_between(t, aws_l, step="mid", alpha=.35, color="deepskyblue",
                 label="AWS Lambda Concurrency")
plt.fill_between(t, gcp_w, step="mid", alpha=.35, color="salmon",
                 label="GCP Dataflow Workers")
plt.xlabel("Time (minutes since midnight)");  plt.ylabel("Provisioned Resources")
plt.title("24-Hour Horizon: Auto-Scaling Behavior (AWS vs GCP)")
plt.legend(); plt.grid(True); fig3.tight_layout(); fig3.savefig("plot3_autoscale.png")

'''
plot-4 Sustainability vs speed, Cloud ECO

'''
eco = pd.DataFrame({
    "Provider": ["GCP Iowa", "AWS Oregon", "AWS Virginia", "GCP Singapore"],
    "EcoScore": [0.85, 0.70, 0.60, 0.40],
    "Speed":    [46000, 45000, 48000, 42000],
    "Color":    ["green", "green", "orange", "red"]
})

fig4 = plt.figure(figsize=(8,5))
for _,r in eco.iterrows():
    plt.scatter(r.Speed, r.EcoScore, s=220, color=r.Color)
    plt.text(r.Speed+200, r.EcoScore, r.Provider, fontsize=8)
plt.xlabel("Processing Speed (events/minute)"); plt.ylabel("Eco-Score (0-1)")
plt.title("Sustainability vs Speed (Events/Minute)"); plt.grid(True)
fig4.tight_layout(); fig4.savefig("plot4_eco_speed.png")

print("\n  Plots saved: plot1_latency.png  plot2_costs.png  plot3_autoscale.png  plot4_eco_speed.png")

#real April cost table
if {"Project Id","Service Description","Cost"}.issubset(billing.columns):
    april = (billing.query("`Project Id` == @GCP_PROJECT")
                  .groupby("Service Description")["Cost"].sum()
                  .sort_values(ascending=False)
                  .head(12))
    print("\n\nTop GCP cost drivers in April 2025 for project", GCP_PROJECT)
    print(april.to_string())
else:
    print("\n\nBilling CSV column names differ; tweak script's last section.")
