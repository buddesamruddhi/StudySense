import calendar
from datetime import date, datetime, timedelta
import io
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

import database as db
import auth
import analytics
import planner

st.set_page_config(page_title="Learn Flow | Student Workload Analyzer", page_icon="📘", layout="wide")
db.init_db()

PRIMARY = "#2563EB"
PURPLE = "#7C3AED"
    
def inject_css(theme):
    if theme == "Dark":
        bg = "#0B1020"
        sidebar = "#10182B"
        card = "#172238"
        text = "#F1F5F9"
        muted = "#A7B4C8"
        border = "#293750"
    else:
        bg = "#F3F6FF"
        sidebar = "#FFFFFF"
        card = "#FFFFFF"
        text = "#172033"
        muted = "#64748B"
        border = "#E1E7F0"

    st.markdown(f"""
    <style>
    .stApp {{
        background:
            radial-gradient(
                circle at top left,
                rgba(37,99,235,0.12),
                transparent 35%
            ),
            {bg};
        color: {text};
    }}

    [data-testid="stSidebar"] {{
        background: {sidebar};
        border-right: 1px solid {border};
    }}

    [data-testid="stSidebar"] h2 {{
        color: #7C3AED;
        font-weight: 850;
    }}

    h1, h2, h3 {{
        color: {text};
        font-weight: 800;
        letter-spacing: -0.5px;
    }}

    div[data-testid="stMetric"] {{
        background: {card};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.08);
        transition: 0.2s ease;
    }}

    div[data-testid="stMetric"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(124, 58, 237, 0.15);
    }}

    .hero {{
        padding: 35px;
        border-radius: 24px;
        color: white;
        background: linear-gradient(
            120deg,
            #2563EB,
            #4F46E5,
            #7C3AED
        );
        box-shadow: 0 15px 35px rgba(79, 70, 229, 0.22);
    }}

    .hero h1,
    .hero h2 {{
        color: white !important;
    }}

    .hero p {{
        color: #E0E7FF !important;
        font-size: 16px;
    }}

    .small-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 22px;
        min-height: 150px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
        transition: 0.2s ease;
    }}

    .small-card:hover {{
        transform: translateY(-4px);
        border-color: #818CF8;
    }}

    div.stButton > button,
    div.stDownloadButton > button {{
        border-radius: 11px;
        font-weight: 650;
        border: 1px solid {border};
        transition: 0.2s ease;
        min-height: 42px;
    }}

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {{
        color: white;
        background: linear-gradient(100deg, #2563EB, #7C3AED);
        border: none;
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.2);
    }}

    div.stButton > button:hover {{
        border-color: #818CF8;
        transform: translateY(-1px);
    }}

    [data-testid="stExpander"] {{
        border: 1px solid {border};
        border-radius: 15px;
        background: {card};
    }}

    [data-testid="stAlert"] {{
        border-radius: 13px;
    }}

    hr {{
        border-color: {border};
    }}
    </style>
    """, unsafe_allow_html=True)


def current_user():
    uid=st.session_state.get("user_id")
    return db.get_user(uid) if uid else None

def go(page):
    st.session_state.page=page
    st.rerun()

def header(title, subtitle=None):
    st.title(title)
    if subtitle: st.caption(subtitle)

def render_landing():
    st.markdown('<div class="hero"><h1>Study Smarter, Balance Better, Achieve More.</h1><p>Track your study habits, organize academic deadlines, understand your workload, and build a smarter study plan.</p></div>', unsafe_allow_html=True)
    st.write("")
    a,b=st.columns([1,1])
    with a:
        if st.button("Get Started", type="primary", use_container_width=True): go("Register")
    with b:
        if st.button("Login", use_container_width=True): go("Login")
    st.subheader("Everything you need to study with a plan")
    cols=st.columns(3)
    features=[("📚","Smart Study Tracking","Record study sessions and compare planned versus actual hours."),
              ("📅","Academic Task Calendar","Plan assignments, exams, revisions, and deadlines."),
              ("📊","Study Pattern Analysis","Explore trends and data-based insights."),
              ("⚖️","Workload Monitoring","Identify upcoming pressure points and overdue tasks."),
              ("📝","Important Notes","Keep academic instructions and ideas in one place."),
              ("🎯","Personalized Study Planner","Build a schedule around pending tasks and available time.")]
    for i,(icon,title,desc) in enumerate(features):
        with cols[i%3]:
            st.markdown(f'<div class="small-card"><h3>{icon} {title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
        if i%3==2: st.write("")
    st.subheader("How it works")
    st.write("**1. Record** your study sessions  →  **2. Organize** your tasks  →  **3. Analyze** your patterns  →  **4. Improve** your schedule")
    st.caption("StudySense is a student productivity tool. Insights are based on recorded information, not medical advice.")

def render_login():
    _,mid,_=st.columns([1,1.15,1])
    with mid:
        st.markdown("## Welcome back")
        st.caption("Log in to continue your study journey.")
        with st.form("login_form"):
            email=st.text_input("Email address")
            password=st.text_input("Password",type="password")
            submitted=st.form_submit_button("Login",type="primary",use_container_width=True)
        if submitted:
            user=auth.login_user(email,password)
            if user:
                st.session_state.user_id=user["id"]
                st.session_state.page="Overview"
                st.rerun()
            else: st.error("Incorrect email or password.")
        if st.button("Create an account"): go("Register")
        if st.button("Back to home"): go("Home")

def render_register():
    _,mid,_=st.columns([1,1.2,1])
    with mid:
        st.markdown("## Create your account")
        st.caption("Start organizing your study routine.")
        with st.form("register_form"):
            name=st.text_input("Full Name")
            email=st.text_input("Email Address")
            password=st.text_input("Password",type="password",help="Use at least 8 characters.")
            confirm=st.text_input("Confirm Password",type="password")
            submitted=st.form_submit_button("Create Account",type="primary",use_container_width=True)
        if submitted:
            try:
                uid=auth.register_user(name,email,password,confirm)
                st.session_state.user_id=uid
                st.session_state.page="Overview"
                st.success("Account created.")
                st.rerun()
            except ValueError as e: st.error(str(e))
        if st.button("Already have an account? Login"): go("Login")
        if st.button("Back to home"): go("Home")

def add_task_form(user_id, default_date=None, task=None, form_key="task_form"):
    task=task or {}
    default_date=default_date or date.today()
    with st.form(form_key):
        c1,c2=st.columns(2)
        title=c1.text_input("Task Title",value=task.get("title",""))
        subject=c2.text_input("Subject",value=task.get("subject",""))
        description=st.text_area("Description",value=task.get("description",""))
        c3,c4,c5=st.columns(3)
        category=c3.selectbox("Category",["Assignment","Examination","Project","Revision","Submission","Personal","Other"],
                              index=["Assignment","Examination","Project","Revision","Submission","Personal","Other"].index(task.get("category","Assignment")) if task.get("category","Assignment") in ["Assignment","Examination","Project","Revision","Submission","Personal","Other"] else 0)
        priority=c4.selectbox("Priority",["High","Medium","Low"],index=["High","Medium","Low"].index(task.get("priority","Medium")) if task.get("priority","Medium") in ["High","Medium","Low"] else 1)
        status=c5.selectbox("Status",["Pending","In Progress","Completed"],index=["Pending","In Progress","Completed"].index(task.get("status","Pending")) if task.get("status","Pending") in ["Pending","In Progress","Completed"] else 0)
        c6,c7,c8=st.columns(3)
        try: sched_default=date.fromisoformat(task.get("scheduled_date") or str(default_date))
        except ValueError: sched_default=default_date
        scheduled=c6.date_input("Scheduled Date",value=sched_default)
        deadline_default=None
        if task.get("deadline"):
            try: deadline_default=date.fromisoformat(task["deadline"])
            except ValueError: pass
        deadline=c7.date_input("Deadline (optional)",value=deadline_default)
        duration=c8.number_input("Estimated Duration (hours)",min_value=0.25,max_value=24.0,value=float(task.get("estimated_duration") or 1),step=0.25)
        c9,c10=st.columns(2)
        start=c9.text_input("Start Time (optional, HH:MM)",value=task.get("start_time",""),placeholder="09:00")
        end=c10.text_input("End Time (optional, HH:MM)",value=task.get("end_time",""),placeholder="10:00")
        save=st.form_submit_button("Save Task",type="primary")
    if save:
        if not title.strip(): st.error("Task title is required."); return
        for t in (start,end):
            if t and (len(t)!=5 or t[2]!=":" or not t[:2].isdigit() or not t[3:].isdigit() or int(t[:2])>23 or int(t[3:])>59):
                st.error("Time must use HH:MM, for example 09:30."); return
        if start and end and end <= start: st.error("End time must be after start time."); return
        data={"title":title,"description":description,"subject":subject,"category":category,
              "scheduled_date":scheduled.isoformat(),"start_time":start,"end_time":end,
              "deadline":deadline.isoformat() if deadline else "","priority":priority,
              "estimated_duration":duration,"status":status}
        try:
            db.save_task(user_id,data,task.get("id"))
            st.success("Task saved.")
            st.rerun()
        except ValueError as e: st.error(str(e))

def render_task_management(user):
    uid=user["id"]
    header("Task Management","Organize assignments, projects, revision, and deadlines.")
    with st.expander("＋ Add Task",expanded=False): add_task_form(uid,form_key="task_add")
    tasks=db.list_tasks(uid)
    if not tasks: st.info("No tasks yet. Add your first academic task above.")
    else:
        a,b,c,d=st.columns(4)
        search=a.text_input("Search title")
        status=b.selectbox("Status",["All","Pending","In Progress","Completed"])
        priority=c.selectbox("Priority",["All","High","Medium","Low"])
        category=d.selectbox("Category",["All","Assignment","Examination","Project","Revision","Submission","Personal","Other"])
        filtered=[]
        for t in tasks:
            if search.lower() not in t["title"].lower(): continue
            if status!="All" and t["status"]!=status: continue
            if priority!="All" and t["priority"]!=priority: continue
            if category!="All" and t["category"]!=category: continue
            filtered.append(t)
        for t in filtered:
            with st.container(border=True):
                col1,col2,col3,col4=st.columns([3,1,1,1])
                col1.markdown(f"**{t['title']}**  \n{t.get('subject') or 'No subject'} · {t['category']} · Scheduled: {t['scheduled_date']}")
                col2.write(f"**{t['priority']}**")
                col3.write(t["status"])
                with col4.popover("Actions"):
                    if st.button("Mark complete",key=f"complete_{t['id']}"):
                        db.set_task_status(uid,t["id"],"Completed"); st.rerun()
                    if st.button("Edit",key=f"edit_task_{t['id']}"):
                        st.session_state.edit_task=t["id"]; st.rerun()
                    if st.button("Delete",key=f"delete_task_{t['id']}"):
                        st.session_state.confirm_delete_task=t["id"]; st.rerun()
                if t.get("deadline"):
                    if t["deadline"] < date.today().isoformat() and t["status"]!="Completed":
                        st.error(f"Overdue · Deadline {t['deadline']}")
                    else: st.caption(f"Deadline: {t['deadline']} · Estimated duration: {t['estimated_duration']} hours")
                if st.session_state.get("edit_task")==t["id"]:
                    with st.expander("Edit task",expanded=True):
                        add_task_form(uid,task=t,form_key=f"task_edit_{t['id']}")
                    if st.button("Close editor",key=f"close_edit_{t['id']}"):
                        st.session_state.pop("edit_task",None); st.rerun()
                if st.session_state.get("confirm_delete_task")==t["id"]:
                    st.warning("Delete this task permanently?")
                    x,y=st.columns(2)
                    if x.button("Confirm delete",key=f"confirm_del_{t['id']}",type="primary"):
                        db.delete_task(uid,t["id"]); st.session_state.pop("confirm_delete_task",None); st.rerun()
                    if y.button("Cancel",key=f"cancel_del_{t['id']}"):
                        st.session_state.pop("confirm_delete_task",None); st.rerun()

def render_calendar(user):
    uid=user["id"]
    header("Task Calendar","Plan academic work and keep deadlines visible.")
    if "calendar_date" not in st.session_state: st.session_state.calendar_date=date.today()
    current=st.session_state.calendar_date
    top1,top2,top3,top4=st.columns([1,1,2,1])
    if top1.button("← Previous"):
        if st.session_state.calendar_view=="Month":
            st.session_state.calendar_date=(current.replace(day=1)-timedelta(days=1)).replace(day=1)
        else: st.session_state.calendar_date=current-timedelta(days=7 if st.session_state.calendar_view=="Week" else 1)
        st.rerun()
    if top2.button("Today"):
        st.session_state.calendar_date=date.today(); st.rerun()
    view=top3.selectbox("Calendar view",["Month","Week","Day"],index=["Month","Week","Day"].index(st.session_state.get("calendar_view","Month")))
    st.session_state.calendar_view=view
    if top4.button("Next →"):
        if view=="Month":
            next_month=(current.replace(day=28)+timedelta(days=4)).replace(day=1)
            st.session_state.calendar_date=next_month
        else: st.session_state.calendar_date=current+timedelta(days=7 if view=="Week" else 1)
        st.rerun()
    with st.expander("＋ Add Task",expanded=False):
        add_task_form(uid,default_date=current,form_key="calendar_add_task")
    tasks=db.list_tasks(uid)
    tasks_by_date={}
    for t in tasks: tasks_by_date.setdefault(t["scheduled_date"],[]).append(t)
    if view=="Month":
        cal=calendar.Calendar(firstweekday=0)
        weeks=cal.monthdatescalendar(current.year,current.month)
        st.markdown(f"### {current.strftime('%B %Y')}")
        names=st.columns(7)
        for col,name in zip(names,["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]): col.markdown(f"**{name}**")
        for week in weeks:
            cols=st.columns(7)
            for col,d in zip(cols,week):
                with col:
                    if d.month!=current.month: st.caption(f"{d.day}")
                    else:
                        label=f"**{d.day}**"
                        if d==date.today(): label+=" · Today"
                        st.markdown(label)
                        daytasks=tasks_by_date.get(d.isoformat(),[])
                        for t in daytasks[:3]:
                            color={"High":"🔴","Medium":"🟠","Low":"🔵"}.get(t["priority"],"🔵")
                            if t["status"]=="Completed": color="🟢"
                            st.caption(f"{color} {t['title'][:17]}")
                        if len(daytasks)>3: st.caption(f"+{len(daytasks)-3} more")
                        if st.button("Select",key=f"select_{d.isoformat()}"):
                            st.session_state.selected_calendar_date=d
                            st.rerun()
    elif view=="Week":
        monday=current-timedelta(days=current.weekday())
        cols=st.columns(7)
        for i,col in enumerate(cols):
            d=monday+timedelta(days=i)
            with col:
                st.markdown(f"**{d.strftime('%a %d')}**")
                for t in tasks_by_date.get(d.isoformat(),[]):
                    st.markdown(f"**{t['title']}**")
                    st.caption(f"{t['start_time'] or 'Unscheduled'} · {t['priority']}")
                if st.button("Select",key=f"week_select_{d.isoformat()}"):
                    st.session_state.selected_calendar_date=d; st.rerun()
    else:
        st.markdown(f"### {current.strftime('%A, %d %B %Y')}")
        for t in tasks_by_date.get(current.isoformat(),[]):
            st.markdown(f"- **{t['start_time'] or 'Unscheduled'}** — {t['title']} ({t['status']}, {t['priority']})")
    selected=st.session_state.get("selected_calendar_date",current)
    if isinstance(selected,str):
        try: selected=date.fromisoformat(selected)
        except ValueError: selected=current
    st.divider()
    st.subheader(f"Tasks for {selected.strftime('%d %B %Y')}")
    daytasks=tasks_by_date.get(selected.isoformat(),[])
    if not daytasks: st.info("No tasks scheduled for this day. Use Add Task to schedule one.")
    for t in daytasks:
        c1,c2,c3=st.columns([4,1,1])
        c1.write(f"**{t['title']}** · {t.get('subject') or 'No subject'}")
        c1.caption(f"{t['category']} · {t['start_time'] or 'No time'} · Deadline: {t['deadline'] or 'Not set'}")
        c2.write(f"{t['priority']} / {t['status']}")
        if c3.button("Complete",key=f"cal_complete_{t['id']}"):
            db.set_task_status(uid,t["id"],"Completed"); st.rerun()
    st.divider()
    st.subheader("Upcoming deadlines")
    today=date.today().isoformat()
    soon=(date.today()+timedelta(days=7)).isoformat()
    pending=[t for t in tasks if t["status"]!="Completed"]
    groups=[("Due Today",[t for t in pending if t.get("deadline")==today]),
            ("Due Tomorrow",[t for t in pending if t.get("deadline")== (date.today()+timedelta(days=1)).isoformat()]),
            ("Due Within 7 Days",[t for t in pending if today < (t.get("deadline") or "") <= soon]),
            ("Overdue",[t for t in pending if t.get("deadline") and t["deadline"]<today])]
    for label,items in groups:
        with st.expander(f"{label} ({len(items)})"):
            if items:
                for t in items: st.write(f"**{t['title']}** — {t['deadline']} · {t['priority']}")
            else: st.caption("Nothing here.")

def render_study_log(user):
    uid=user["id"]
    header("Study Log","Record study sessions and compare your plans with actual progress.")
    with st.expander("＋ Add Study Session",expanded=not bool(db.list_logs(uid))):
        with st.form("study_log_form"):
            c1,c2=st.columns(2)
            study_date=c1.date_input("Study Date",value=date.today())
            subject=c2.text_input("Subject")
            topic=st.text_input("Topic or Activity")
            c3,c4,c5=st.columns(3)
            planned=c3.number_input("Planned Study Hours",0.0,24.0,1.0,0.25)
            actual=c4.number_input("Actual Study Hours",0.0,24.0,1.0,0.25)
            sleep=c5.number_input("Sleep Duration (hours)",0.0,24.0,7.0,0.25)
            c6,c7=st.columns(2)
            assigned=c6.number_input("Tasks Assigned",0,100,1)
            completed=c7.number_input("Tasks Completed",0,100,1)
            method=st.selectbox("Study Method",["Reading","Practice","Video Lecture","Revision","Assignment","Other"])
            notes=st.text_area("Optional Notes")
            save=st.form_submit_button("Save Session",type="primary")
        if save:
            if not subject.strip() or not topic.strip(): st.error("Subject and topic are required.")
            elif completed>assigned: st.error("Tasks completed cannot exceed tasks assigned.")
            else:
                db.save_log(uid,{"study_date":study_date.isoformat(),"subject":subject.strip(),"topic":topic.strip(),
                    "planned_hours":planned,"actual_hours":actual,"tasks_assigned":assigned,"tasks_completed":completed,
                    "sleep_hours":sleep,"study_method":method,"notes":notes})
                st.success("Study session saved."); st.rerun()
    logs=db.list_logs(uid)
    if logs:
        df=pd.DataFrame(logs)
        c1,c2,c3=st.columns(3)
        search=c1.text_input("Search subject or topic")
        start=c2.date_input("From date",value=date.today()-timedelta(days=30),key="log_from")
        end=c3.date_input("To date",value=date.today(),key="log_to")
        df["date_obj"]=pd.to_datetime(df["study_date"],errors="coerce")
        df=df[(df["date_obj"].dt.date>=start)&(df["date_obj"].dt.date<=end)]
        df=df[df["subject"].str.contains(search,case=False,na=False)|df["topic"].str.contains(search,case=False,na=False)]
        show=df[["study_date","subject","topic","planned_hours","actual_hours","tasks_assigned","tasks_completed","sleep_hours","study_method","notes"]]
        st.dataframe(show, use_container_width=True, hide_index=True)
        csv=show.to_csv(index=False).encode("utf-8")
        st.download_button("Export filtered study logs CSV",csv,"study_logs.csv","text/csv")
        with st.expander("Delete a study session"):
            options={f"#{r['id']} · {r['study_date']} · {r['subject']} — {r['topic']}":r["id"] for r in logs}
            selected=st.selectbox("Choose session",list(options))
            if st.button("Delete selected session"):
                db.delete_log(uid,options[selected]); st.rerun()
    else: st.info("No study sessions yet. Add your first session above.")

def render_pattern_analysis(user):
    header("Pattern Analysis","Understand your study habits using your recorded data.")
    logs=db.list_logs(user["id"]); df=analytics.logs_frame(logs)
    if df.empty:
        st.info("Record at least one study session to see your personal charts and insights.")
        return
    a,b,c,d=st.columns(4)
    a.metric("Average daily study",f"{df.groupby(df.study_date.dt.date).actual_hours.sum().mean():.1f} h")
    b.metric("Most studied subject",df.groupby("subject").actual_hours.sum().idxmax())
    weekday=df.groupby(df.study_date.dt.day_name()).actual_hours.mean()
    c.metric("Highest logged weekday",weekday.idxmax())
    consistency=(df.groupby(df.study_date.dt.date).actual_hours.sum()>0).mean()*100
    d.metric("Logged-day consistency",f"{consistency:.0f}%")
    left,right=st.columns(2)
    with left:
        daily=df.groupby(df.study_date.dt.date).actual_hours.sum()
        st.subheader("Study hours by date")
        st.bar_chart(daily)
        st.subheader("Study hours by subject")
        st.bar_chart(df.groupby("subject").actual_hours.sum())
    with right:
        st.subheader("Planned vs actual")
        st.bar_chart(df.groupby(df.study_date.dt.date)[["planned_hours","actual_hours"]].sum())
        st.subheader("Task completion trend")
        df["completion"]=(df.tasks_completed/df.tasks_assigned.replace(0,1))*100
        st.line_chart(df.groupby(df.study_date.dt.date).completion.mean())
    st.subheader("Insights")
    for insight in analytics.data_insights(logs,db.list_tasks(user["id"])): st.info(insight)

def render_workload(user):
    header("Workload Analysis","Review pending work, deadlines, and practical workload signals.")
    logs=db.list_logs(user["id"]); tasks=db.list_tasks(user["id"])
    result=analytics.workload_assessment(logs,tasks)
    color={"Low":"🟢","Moderate":"🟠","High":"🔴"}[result["level"]]
    st.markdown(f"## {color} {result['level']} workload risk")
    a,b,c,d=st.columns(4)
    a.metric("Pending Tasks",result["pending"])
    b.metric("Overdue Tasks",result["overdue"])
    c.metric("Due in 3 Days",result["due_soon"])
    d.metric("Task Completion",f"{result['completion']}%")
    left,right=st.columns(2)
    with left:
        st.subheader("Risk factors")
        for reason in result["reasons"]: st.write(f"- {reason}")
        st.subheader("Recommended actions")
        if result["overdue"]: st.write("- Review overdue tasks and renegotiate or reschedule deadlines where appropriate.")
        if result["due_soon"]>=3: st.write("- Prioritize urgent work and split large tasks into smaller sessions.")
        if result["pending"]>=4: st.write("- Move lower-priority work to less busy days.")
        if result["avg_actual"]>6: st.write("- Check whether your planned study schedule is sustainable.")
        if result["avg_sleep"] and result["avg_sleep"]<6: st.write("- Review your schedule to protect adequate rest.")
        if result["level"]=="Low": st.write("- Keep recording sessions and review your workload weekly.")
    with right:
        st.subheader("Pending tasks by priority")
        if tasks:
            df=pd.DataFrame([t for t in tasks if t["status"]!="Completed"])
            if not df.empty: st.bar_chart(df.groupby("priority").size())
            else: st.success("All tasks are completed.")
        else: st.info("Add tasks to see workload distribution.")
        st.subheader("Upcoming deadlines")
        today=date.today().isoformat()
        soon=(date.today()+timedelta(days=7)).isoformat()
        for t in tasks:
            if t["status"]!="Completed" and t.get("deadline") and t["deadline"]<=soon:
                st.write(f"**{t['title']}** — {t['deadline']} · {t['priority']}")
    st.caption("Workload risk is a transparent heuristic based on recorded data, not a medical or validated predictive assessment.")

def render_notes(user):
    uid=user["id"]
    header("Important Notes","Save academic instructions, ideas, and reminders in one place.")
    with st.expander("＋ Create Note",expanded=False):
        with st.form("create_note_form"):
            title=st.text_input("Note Title")
            content=st.text_area("Note Content",height=130)
            category=st.selectbox("Category",["General","Assignment","Exam","Project","Meeting","Personal","Other"])
            pinned=st.checkbox("Pin this note")
            save=st.form_submit_button("Save Note",type="primary")
        if save:
            if not title.strip() or not content.strip(): st.error("Title and content are required.")
            else: db.save_note(uid,title,content,category,pinned); st.success("Note saved."); st.rerun()
    notes=db.list_notes(uid)
    search=st.text_input("Search notes")
    categories=["All"]+sorted({n["category"] for n in notes})
    category=st.selectbox("Filter by category",categories)
    filtered=[n for n in notes if search.lower() in (n["title"]+" "+n["content"]).lower() and (category=="All" or n["category"]==category)]
    if not filtered: st.info("Your notes will appear here. Save important academic instructions, project ideas, and reminders.")
    cols=st.columns(3)
    for i,n in enumerate(filtered):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown(("📌 " if n["pinned"] else "")+f"**{n['title']}**")
                st.caption(f"{n['category']} · Updated {n['updated_at']}")
                st.write(n["content"][:350]+("…" if len(n["content"])>350 else ""))
                with st.expander("Edit note"):
                    with st.form(f"edit_note_{n['id']}"):
                        nt=st.text_input("Title",n["title"])
                        nc=st.text_area("Content",n["content"])
                        cats=["General","Assignment","Exam","Project","Meeting","Personal","Other"]
                        ix=cats.index(n["category"]) if n["category"] in cats else 0
                        cat=st.selectbox("Category",cats,index=ix)
                        pin=st.checkbox("Pin this note",value=bool(n["pinned"]))
                        save=st.form_submit_button("Update Note")
                    if save:
                        if nt.strip() and nc.strip():
                            db.save_note(uid,nt,nc,cat,pin,n["id"]); st.success("Updated."); st.rerun()
                        else: st.error("Title and content are required.")
                if st.button("Delete note",key=f"note_del_{n['id']}"):
                    st.session_state.confirm_delete_note=n["id"]
                if st.session_state.get("confirm_delete_note")==n["id"]:
                    st.warning("Delete this note?")
                    x,y=st.columns(2)
                    if x.button("Confirm",key=f"note_confirm_{n['id']}"):
                        db.delete_note(uid,n["id"]); st.session_state.pop("confirm_delete_note",None); st.rerun()
                    if y.button("Cancel",key=f"note_cancel_{n['id']}"):
                        st.session_state.pop("confirm_delete_note",None); st.rerun()

def render_planner(user):
    uid=user["id"]
    header("Study Planner","Create a practical schedule from pending tasks and your available study time.")
    tasks=db.list_tasks(uid)
    with st.form("planner_settings"):
        c1,c2,c3=st.columns(3)
        start=c1.date_input("Start Date",value=date.today())
        days=c2.number_input("Planning Period (days)",1,30,int(user.get("planning_days",7)))
        daily=c3.number_input("Available Study Hours per Day",0.5,16.0,float(user.get("daily_limit",5)),0.5)
        c4,c5=st.columns(2)
        session=c4.number_input("Preferred Session Duration (minutes)",15,180,int(user.get("session_minutes",45)),5)
        break_mins=c5.number_input("Preferred Break Duration (minutes)",0,60,int(user.get("break_minutes",10)),5)
        submitted=st.form_submit_button("Generate Study Plan",type="primary")
    if submitted:
        db.update_settings(uid,(daily,session,break_mins,days,user.get("theme","Light")))
        user=db.get_user(uid)
        generated=planner.generate_plan(user,tasks,start,days)
        db.clear_plans(uid)
        for p in generated: db.add_plan(uid,p["date"],p["subject"],p["title"],p["start"],p["end"],p["duration"])
        st.success("Study plan generated and saved.")
    plans=db.list_plans(uid)
    if plans:
        df=pd.DataFrame(plans)
        st.subheader("Your schedule")
        st.dataframe(df[["plan_date","start_time","end_time","subject","task_title","duration","status"]],use_container_width=True,hide_index=True)
        st.download_button("Export plan CSV",df.to_csv(index=False).encode("utf-8"),"study_plan.csv","text/csv")
        st.caption("This is a suggested schedule. Review and adjust it to avoid conflicts and account for your real commitments.")
    else:
        st.info("Set your available hours and generate a plan. Add tasks first for a task-based schedule.")
    if tasks:
        st.subheader("Tasks considered")
        st.write(", ".join(t["title"] for t in tasks if t["status"]!="Completed") or "No pending tasks.")

def render_reports(user):
    header("Insights & Reports","Review progress and export your study records.")
    uid=user["id"]; logs=db.list_logs(uid); tasks=db.list_tasks(uid)
    start=st.date_input("Report start date",value=date.today()-timedelta(days=30),key="report_start")
    end=st.date_input("Report end date",value=date.today(),key="report_end")
    df=pd.DataFrame(logs)
    if not df.empty:
        df["study_date"]=pd.to_datetime(df["study_date"],errors="coerce")
        filtered=df[(df.study_date.dt.date>=start)&(df.study_date.dt.date<=end)]
        st.subheader("Study summary")
        a,b,c=st.columns(3)
        a.metric("Study Hours",f"{filtered['actual_hours'].sum():.1f}")
        b.metric("Planned Hours",f"{filtered['planned_hours'].sum():.1f}")
        c.metric("Sessions",len(filtered))
        st.bar_chart(filtered.groupby("subject")["actual_hours"].sum() if not filtered.empty else pd.Series(dtype=float))
        export=filtered.drop(columns=["study_date"],errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button("Export study logs CSV",export,"study_report.csv","text/csv")
    else: st.info("Record study sessions to build reports.")
    if tasks:
        tdf=pd.DataFrame(tasks)
        st.subheader("Task summary")
        st.write(tdf["status"].value_counts())
        st.download_button("Export task data CSV",tdf.to_csv(index=False).encode("utf-8"),"task_report.csv","text/csv")
    if st.button("Print-friendly summary"):
        st.markdown("### StudySense Progress Report")
        st.write(f"Period: {start} to {end}")
        st.write(f"Study sessions: {len(logs)} · Tasks: {len(tasks)}")
        st.info("Use your browser's Print command to print this summary.")

def render_settings(user):
    uid=user["id"]
    header("Settings","Manage your profile, appearance, study preferences, and account.")
    st.subheader("Profile")
    st.write(f"**Name:** {user['full_name']}")
    st.write(f"**Email:** {user['email']}")
    st.caption("Profile editing and password reset can be added as a future extension; account passwords are stored as secure hashes.")
    st.subheader("Appearance and study preferences")
    with st.form("settings_form"):
        theme=st.selectbox("Theme",["Light","Dark"],index=0 if user.get("theme","Light")=="Light" else 1)
        daily=st.number_input("Daily Study Hour Limit",0.5,16.0,float(user.get("daily_limit",5)),0.5)
        session=st.number_input("Default Session Duration (minutes)",15,180,int(user.get("session_minutes",45)),5)
        breaks=st.number_input("Default Break Duration (minutes)",0,60,int(user.get("break_minutes",10)),5)
        days=st.number_input("Default Planning Period (days)",1,30,int(user.get("planning_days",7)))
        if st.form_submit_button("Save Settings",type="primary"):
            db.update_settings(uid,(daily,session,breaks,days,theme))
            st.success("Settings saved."); st.rerun()
    st.subheader("Reminders")
    st.info("Upcoming deadlines are shown in Task Calendar. This local version does not send background email or push notifications.")
    st.subheader("Account")
    if st.button("Logout"):
        st.session_state.clear(); st.session_state.page="Home"; st.rerun()
    with st.expander("Delete account"):
        st.warning("This permanently deletes your account and associated records.")
        confirm=st.checkbox("I understand this action cannot be undone.")
        if st.button("Delete my account",type="primary",disabled=not confirm):
            for table in ["study_logs","tasks","notes","plans"]:
                db.execute(f"DELETE FROM {table} WHERE user_id=?", (uid,))
            db.execute("DELETE FROM users WHERE id=?", (uid,))
            st.session_state.clear(); st.session_state.page="Home"; st.rerun()

def render_overview(user):
    uid=user["id"]; logs=db.list_logs(uid); tasks=db.list_tasks(uid)
    header("Overview", "Your study and workload overview.")
    st.markdown(f'<div class="hero"><h2>Good day, {user["full_name"].split()[0]}!</h2><p>Small consistent steps build strong study habits. Here is your current progress.</p></div>',unsafe_allow_html=True)
    risk=analytics.workload_assessment(logs,tasks)
    completed=sum(t["status"]=="Completed" for t in tasks)
    pending=sum(t["status"]!="Completed" for t in tasks)
    df=analytics.logs_frame(logs)
    total=float(df["actual_hours"].sum()) if not df.empty else 0
    avg=float(df.groupby(df.study_date.dt.date).actual_hours.sum().mean()) if not df.empty else 0
    cols=st.columns(3)
    cols[0].metric("Total Study Hours",f"{total:.1f} h")
    cols[1].metric("Completed Tasks",completed)
    cols[2].metric("Pending Tasks",pending)
    cols=st.columns(3)
    cols[0].metric("Task Completion Rate",f"{risk['completion']:.0f}%")
    cols[1].metric("Average Study / Day",f"{avg:.1f} h")
    cols[2].metric("Workload Risk",risk["level"])
    left,right=st.columns(2)
    with left:
        st.subheader("Weekly Study Hours")
        if not df.empty:
            recent=df[df.study_date>=pd.Timestamp(date.today()-timedelta(days=6))]
            st.bar_chart(recent.groupby(recent.study_date.dt.day_name()).actual_hours.sum())
        else: st.caption("Add study sessions to populate this chart.")
        st.subheader("Study Time by Subject")
        if not df.empty: st.bar_chart(df.groupby("subject").actual_hours.sum())
        else: st.caption("Your subject chart will appear here.")
    with right:
        st.subheader("Planned vs Actual")
        if not df.empty: st.bar_chart(df.groupby(df.study_date.dt.date)[["planned_hours","actual_hours"]].sum())
        else: st.caption("Track a session to compare planned and actual hours.")
        st.subheader("Today's Schedule")
        today=date.today().isoformat()
        todays=[t for t in tasks if t["scheduled_date"]==today]
        if todays:
            for t in todays: st.write(f"- **{t['start_time'] or 'Unscheduled'}** {t['title']} · {t['status']}")
        else: st.caption("No tasks scheduled for today.")
    st.subheader("Upcoming Tasks")
    upcoming=sorted([t for t in tasks if t["status"]!="Completed"],key=lambda t:t.get("deadline") or t["scheduled_date"])[:5]
    if upcoming:
        st.dataframe(pd.DataFrame([{"Task":t["title"],"Subject":t["subject"],"Scheduled":t["scheduled_date"],
                                    "Deadline":t["deadline"],"Priority":t["priority"],"Status":t["status"]} for t in upcoming]),
                     use_container_width=True,hide_index=True)
    else: st.info("Add a task to see upcoming work.")
    st.subheader("Quick Actions")
    actions=st.columns(5)
    for col,label,page in zip(actions,["Add Study Session","Add Task","Open Calendar","Create Note","Generate Study Plan"],
                              ["Study Log","Task Management","Task Calendar","Important Notes","Study Planner"]):
        if col.button(label,use_container_width=True): go(page)

def main():
    if "page" not in st.session_state: st.session_state.page="Home"
    user=current_user()
    if user:
        inject_css(user.get("theme","Light"))
        pages=["Overview","Study Log","Pattern Analysis","Workload Analysis","Task Management","Task Calendar",
               "Important Notes","Study Planner","Insights & Reports","Settings"]
        with st.sidebar:
            st.markdown("## 📘 StudySense")
            st.caption("Study Smarter. Balance Better.")
            selected=st.radio("Navigation",pages,index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
            if selected!=st.session_state.page:
                st.session_state.page=selected
                st.rerun()
            st.divider()
            st.write(f"👤 **{user['full_name']}**")
            st.caption(user["email"])
            if st.button("Logout",use_container_width=True):
                st.session_state.clear(); st.session_state.page="Home"; st.rerun()
        page=st.session_state.page
        routes={"Overview":render_overview,"Study Log":render_study_log,"Pattern Analysis":render_pattern_analysis,
                "Workload Analysis":render_workload,"Task Management":render_task_management,"Task Calendar":render_calendar,
                "Important Notes":render_notes,"Study Planner":render_planner,"Insights & Reports":render_reports,
                "Settings":render_settings}
        routes.get(page,render_overview)(user)
    else:
        inject_css("Light")
        with st.sidebar:
            st.markdown("## 📘 StudySense")
            selected=st.radio("Menu",["Home","Login","Register"])
            if selected!=st.session_state.page:
                st.session_state.page=selected
                st.rerun()
        if st.session_state.page=="Login": render_login()
        elif st.session_state.page=="Register": render_register()
        else: render_landing()

if __name__=="__main__":
    main()
