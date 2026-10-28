# Student Workload and Study Pattern Analyzer

A beginner-friendly Python + Streamlit project for tracking study sessions, organizing tasks, viewing an academic calendar, saving important notes, analyzing study patterns, generating a task-based study plan, and exporting reports.

## Features
- Landing page, secure signup/login, password hashing, logout
- User-specific SQLite records
- Study logs with subject, topic, planned/actual hours, tasks, sleep duration, method, and notes
- Study pattern charts and data-driven insights
- Transparent workload risk heuristic
- Task management with duplicate-title prevention per user
- Month/week/day task calendar and upcoming deadline groups
- Important Notes CRUD, search, category filtering, and pinning
- Study plan generation from pending tasks and available hours
- CSV exports and reports
- Light/dark theme preference
- Responsive Streamlit layout

## Requirements
- Python 3.10 or newer recommended
- VS Code
- Internet connection for the first package installation

## Setup in VS Code (Windows)
1. Extract this ZIP file.
2. Open the extracted `study_workload_analyzer` folder in VS Code.
3. Open Terminal → New Terminal.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

5. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this once in the terminal, then activate again:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

6. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

7. Run the app:

   ```powershell
   streamlit run app.py
   ```

8. Open the local URL shown in the terminal, usually `http://localhost:8501`.
9. Register your own account. No default username or password is included.

## Database
The app creates `study_analyzer.db` in this folder on first run. Keep this file to preserve your data. Do not share it because it contains user records. Back it up before moving or modifying the project.

## Notes and limitations
- This is a local academic project, not a security-audited production service.
- Passwords are stored as Werkzeug password hashes.
- Data access queries are scoped by the signed-in user.
- Duplicate task titles are blocked per user after trimming/collapsing spaces and ignoring case.
- The workload rating is a transparent heuristic, not a medically validated assessment.
- The Random Forest dependency is available for future model experiments; the core app does not claim model accuracy.
- Streamlit does not provide background push/email notifications by default. Deadline reminders appear inside the app.
- The calendar has month/week/day layouts. The week/day views are lightweight schedule views rather than a full drag-and-drop calendar.
- Password reset, email verification, and editing profile name/email are not implemented in this local starter.
