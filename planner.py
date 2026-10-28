from datetime import date, timedelta, datetime
import database as db

def generate_plan(user, tasks, start_date=None, days=None):
    start_date = start_date or date.today()
    days = days or int(user.get("planning_days", 7))
    daily_limit = float(user.get("daily_limit", 5))
    session = max(15, int(user.get("session_minutes",45)))
    break_mins = max(0, int(user.get("break_minutes",10)))
    pending = [t for t in tasks if t.get("status") != "Completed"]
    pending.sort(key=lambda t: (0 if t.get("priority")=="High" else 1 if t.get("priority")=="Medium" else 2,
                                t.get("deadline") or "9999-12-31", t.get("scheduled_date") or "9999-12-31"))
    schedule=[]
    minutes_per_day=max(0,int(daily_limit*60))
    day_used={start_date+timedelta(days=i):0 for i in range(days)}
    for task in pending:
        duration=max(0.25,float(task.get("estimated_duration") or 1))
        needed=int(duration*60)
        for d in day_used:
            if needed <= 0: break
            available=minutes_per_day-day_used[d]
            if available <= 0: continue
            allocated=min(needed,available,session)
            if allocated < 15: continue
            start_min=9*60+day_used[d]+(day_used[d]//session)*break_mins
            start_min=min(start_min, 20*60-allocated)
            end_min=start_min+allocated
            schedule.append({"date":d.isoformat(),"subject":task.get("subject") or "General",
                "title":task["title"],"start":f"{start_min//60:02d}:{start_min%60:02d}",
                "end":f"{end_min//60:02d}:{end_min%60:02d}","duration":round(allocated/60,2)})
            day_used[d]+=allocated+break_mins
            needed-=allocated
    if not schedule:
        # Give a simple revision slot if there are no pending tasks.
        for i in range(days):
            d=start_date+timedelta(days=i)
            schedule.append({"date":d.isoformat(),"subject":"Revision","title":"Review class notes",
                             "start":"09:00","end":f"{min(10,9+session//60):02d}:{session%60:02d}",
                             "duration":round(session/60,2)})
    return schedule
