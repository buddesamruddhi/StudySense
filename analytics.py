from datetime import date, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def logs_frame(logs):
    df = pd.DataFrame(logs)
    if df.empty:
        return df
    df["study_date"] = pd.to_datetime(df["study_date"], errors="coerce")
    for col in ["planned_hours","actual_hours","tasks_assigned","tasks_completed","sleep_hours"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

def tasks_frame(tasks):
    df = pd.DataFrame(tasks)
    if df.empty:
        return df
    for col in ["scheduled_date","deadline"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def workload_assessment(logs, tasks):
    today = date.today()
    pending = [t for t in tasks if t.get("status") != "Completed"]
    overdue = [t for t in pending if t.get("deadline") and t["deadline"] < today.isoformat()]
    due_soon = [t for t in pending if t.get("deadline") and today.isoformat() <= t["deadline"] <= (today+timedelta(days=3)).isoformat()]
    df = logs_frame(logs)
    avg_actual = float(df["actual_hours"].mean()) if not df.empty else 0
    avg_sleep = float(df["sleep_hours"].mean()) if not df.empty else 0
    completion = (sum(int(t.get("status") == "Completed") for t in tasks) / len(tasks) * 100) if tasks else 0
    score = 0
    reasons = []
    if len(pending) >= 8: score += 2; reasons.append("Many pending tasks")
    elif len(pending) >= 4: score += 1; reasons.append("Several pending tasks")
    if len(overdue) >= 1: score += 2; reasons.append(f"{len(overdue)} overdue task(s)")
    if len(due_soon) >= 3: score += 2; reasons.append("Several deadlines in the next 3 days")
    if avg_actual > 0 and avg_actual > 6: score += 1; reasons.append("Recorded study time is high")
    if avg_sleep > 0 and avg_sleep < 6: score += 1; reasons.append("Recorded average sleep is below 6 hours")
    if tasks and completion < 40: score += 1; reasons.append("Task completion rate is low")
    level = "High" if score >= 4 else "Moderate" if score >= 2 else "Low"
    return {"level": level, "score": score, "pending":len(pending), "overdue":len(overdue),
            "due_soon":len(due_soon), "completion":round(completion,1), "avg_actual":round(avg_actual,1),
            "avg_sleep":round(avg_sleep,1), "reasons":reasons or ["No major risk indicators in the available records."]}

def data_insights(logs, tasks):
    insights=[]
    df=logs_frame(logs)
    if df.empty:
        insights.append("Add study sessions to receive insights based on your own data.")
    else:
        if len(df) >= 2:
            daily = df.groupby(df["study_date"].dt.day_name())["actual_hours"].mean().sort_values(ascending=False)
            if not daily.empty:
                insights.append(f"Your highest average study time is on {daily.index[0]} ({daily.iloc[0]:.1f} hours per logged session).")
        planned = df["planned_hours"].sum()
        actual = df["actual_hours"].sum()
        if planned > 0:
            diff = planned-actual
            if diff > 1: insights.append(f"You recorded {diff:.1f} fewer study hours than planned.")
            elif diff < -1: insights.append(f"You studied {abs(diff):.1f} hours more than planned. Review whether your plan is realistic.")
            else: insights.append("Your recorded study time is close to your planned total.")
        if df["subject"].nunique():
            top = df.groupby("subject")["actual_hours"].sum().sort_values(ascending=False)
            insights.append(f"Your most-studied subject is {top.index[0]} ({top.iloc[0]:.1f} hours).")
    if tasks:
        completed=sum(t["status"]=="Completed" for t in tasks)
        insights.append(f"You have completed {completed} of {len(tasks)} recorded tasks.")
    else:
        insights.append("Add academic tasks to see task-completion insights.")
    return insights

def train_demo_model(logs):
    """Optional illustrative model; use only if there are enough records with both labels."""
    df=logs_frame(logs)
    if len(df)<20:
        return None, "Record at least 20 study sessions before attempting a demo model."
    df["label"]=(df["actual_hours"] >= df["planned_hours"]).astype(int)
    if df["label"].nunique()<2:
        return None, "The current records contain only one outcome class; a model cannot be trained reliably."
    X=df[["planned_hours","actual_hours","tasks_assigned","tasks_completed","sleep_hours"]].fillna(0)
    model=RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X,df["label"])
    return model, "Illustrative model trained on your recorded sessions. This is not a validated prediction."
