"""
Full Footplate Inspection Form (Parts A/B/C) - Supabase integration
- Employee lookup/create
- Save inspection metadata and per-item scores
- Redirect to dashboard after successful save
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except Exception:
    # supabase not installed - handle gracefully
    create_client = None
    Client = None
    SUPABASE_AVAILABLE = False
import os
from dotenv import load_dotenv
import socket
import platform
import time

# Load environment variables
load_dotenv()

# Basic styling
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; margin-bottom: 10px; }
    .section-title { font-size: 1.1rem; font-weight: 600; margin-top: 8px; }
    .success-message { background-color: #d4edda; color: #155724; padding: 0.6rem; border-radius: 6px; }
    .error-message { background-color: #f8d7da; color: #721c24; padding: 0.6rem; border-radius: 6px; }
    table.rt-table { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase() -> Client:
    # Check library availability first
    if not SUPABASE_AVAILABLE:
        st.error(
            "Python package 'supabase' is not installed. Install it with:\n\n"
            "pip install supabase python-dotenv\n\n"
            "Or run: pip install -r requirements.txt\n\n"
            "After installation, restart Streamlit."
        )
        return None

    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

# Helpers
def get_device_info():
    try:
        return f"{platform.system()} {platform.release()}"
    except:
        return "Unknown"

def get_ip_address():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "Unknown"

def get_employee(supabase, emp_id):
    r = supabase.table("employees").select("*").eq("employee_id", emp_id).limit(1).execute()
    if r and r.data:
        return r.data[0]
    return None

def create_employee(supabase, emp_id, name):
    payload = {"employee_id": emp_id, "name": name}
    r = supabase.table("employees").insert(payload).execute()
    if r and r.data:
        return r.data[0]
    return None

def create_inspection_and_scores(supabase, meta, scores):
    # Insert inspection metadata
    res = supabase.table("footplate_inspections").insert(meta).execute()
    if hasattr(res, 'error') and res.error:
        return False, str(res.error)
    if not res or not res.data:
        return False, "Failed to create inspection record"
    inspection_id = res.data[0]["id"]

    # Attach inspection id to scores and bulk insert
    for s in scores:
        s["inspection_id"] = inspection_id
    res2 = supabase.table("inspection_scores").insert(scores).execute()
    if hasattr(res2, 'error') and res2.error:
        # Optionally delete the inspection record to keep consistent
        supabase.table("footplate_inspections").delete().eq("id", inspection_id).execute()
        return False, str(res2.error)

    return True, inspection_id

# Define parts and items (using provided lists)
PARTS = [
    {
        "part": "A",
        "section": "Driving Skill",
        "items": [
            "Starting /Stopping of train (Jerk free)",
            "Completing all pre departure checks within the specified time",
            "Activation & Deactivation of train Mainline/Depot",
            "Verifying status of door closure before departure",
            "Habit of checking of faults when pop up",
            "Efficient troubleshooting of train defects",
            "correct & precise reporting of faults to OCC/DCC",
            "Ensuring movement as per timetable",
            "Proper Response to the advisory/Target speed",
            "Docking at NSP",
            "Verifying door opening from available indications",
            "Adequate information to passengers",
            "Response to wheel slip/ slide",
            "Observing Neural section Movement",
            "Verifying safety switch status"
        ],
        "max": 1
    },
    {
        "part": "A",
        "section": "Safety",
        "items": [
            "Following proper sign ON /Off Procedure",
            "Notice Board Reading",
            "Not using Mobile phone during driving",
            "Train Preparation as per guidelines",
            "Verifies safety switch positions and confirm same on radio",
            "Handing over & taking over of train",
            "Cab leaving procedure",
            "Not carrying any unauthorized person in cab",
            "Calling Out aspect of line side signal",
            "Proper radio Communication",
            "Respect to signal",
            "Attentive during platform entry & exit",
            "Vigilant towards track, OHE & Surroundings",
            "Following procedure during degraded mode of operation",
            "Attentive while taking charge of train"
        ],
        "max": 1
    },
    {
        "part": "A",
        "section": "Communication",
        "items": [
            "Proper information played for passengers",
            "Proper communication with passenger in case emergency alarm",
            "Proper acknowledgement of message from OCC/DCC",
            "Standard communication during movement",
            "Standard communication during Depot Entry / Exit"
        ],
        "max": 1
    },
    {
        "part": "B",
        "section": "Safety & Operating Knowledge",
        "items": [
            "Knowledge of organization culture, vision & mission",
            "Operating Procedure in degraded mode",
            "Knowledge of latest Circular, SOP",
            "Knowledge of different parts of train",
            "Knowledge of working of train during foggy weather / low visibility",
            "Knowledge of Depot layout/point setting during movement",
            "Knowledge of different speed restrictions in circumstances",
            "Knowledge of undershoot/overshoot movement",
            "Movement during blank signal/defective signal/during signal aspect permissive but not desired",
            "Knowledge of different hand signals",
            "Knowledge of current timetable",
            "Knowledge of different PSR/TSR",
            "Knowledge of different Emergency staircase",
            "Knowledge of movement during communication failure",
            "Knowledge of different emergency communication"
        ],
        "max": 1
    },
    {
        "part": "B",
        "section": "Technical Knowledge",
        "items": [
            "Various Control & Information available on TCMS",
            "Coupling Procedure",
            "Door Failure",
            "PEA Operations",
            "Smoke Detection",
            "ETCS / RS EB recognition",
            "Failure of Train Radio",
            "Traction Failures",
            "Brake system Failures",
            "Evacuation Procedure"
        ],
        "max": 1
    },
    {
        "part": "C",
        "section": "Rating by Nominated Line Manager",
        "items": [
            "Any failure, showing lack of safety consciousness or accidents or mistakes or violation of SOP/ Rules.",
            "Alcoholic/smocking habit",
            "Courteous behaviour and willingness to provide due help to the passenger",
            "Clean & tidy appearance",
            "Proper uniform with name badge",
            "Punctuality & attitude towards work",
            "Duty consciousness, sincerity & hardworking",
            "Reporting of irregularities on mainline",
            "Maintenance of Memo book, SOPs & Instruction etc.",
            "Gentle handling of equipment and other official objects",
            "Ability to handle pressure situation",
            "Patience & ability to concentrate",
            "Respect towards seniors and peers & compassion towards juniors",
            "Presence for duty/no absence on medical ground",
            "Commitment to the organization's Vision & Mission",
            "Willingness to acquire new knowledge & skills",
            "Keeping oneself updated with relevant rules & procedures",
            "Preparedness to handle disaster/emergency",
            "Awareness for personal safety",
            "Proper upkeep of kit bag with all its required belongings"
        ],
        "max": 2
    }
]

# Main
def main():

    supabase = init_supabase()
    if not supabase:
        return

    # Helper: logout and prompt re-login
    def handle_jwt_expired():
        from auth import logout
        logout()
        st.error("Session expired. Please log in again.")
        st.stop()

    # Fetch all employees for dropdown
    @st.cache_data(ttl=60)
    def get_all_employees(_supabase):
        r = _supabase.table("employees").select("employee_id, name, designation").execute()
        return r.data if r and r.data else []

    try:
        employees = get_all_employees(supabase)
    except Exception as e:
        if 'JWT expired' in str(e):
            handle_jwt_expired()
        else:
            st.error(f"Error loading employees: {e}")
            return
    emp_id_list = [emp['employee_id'] for emp in employees]
    emp_dict = {emp['employee_id']: emp for emp in employees}

    # Employee block
    st.markdown("### 👤 Employee & Inspection Info")
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        selected_emp_id = st.selectbox("Employee ID (Unique)", emp_id_list, index=0 if emp_id_list else None, key="form_employee_selectbox")
    with col2:
        selected_emp = emp_dict.get(selected_emp_id) if selected_emp_id else None
        employee_name = st.text_input("Employee Name", value=selected_emp['name'] if selected_emp else "", disabled=True, key="form_employee_name")
        designation = st.text_input("Designation", value=selected_emp.get('designation', "") if selected_emp else "", disabled=True, key="form_designation")
        st.markdown(f"<span style='color: #888;'>Designation: {designation}</span>", unsafe_allow_html=True)
    with col3:
        lookup = st.button("Lookup", key="form_lookup_button")

    employee_id = selected_emp_id

    inspection_date = st.date_input("Inspection Date", value=datetime.now(), key="form_inspection_date")

    # Render parts dynamically and collect scores
    st.markdown("### 🧾 Assessment Items")

    score_inputs = []  # list of dicts {part, section, item_no, text, max, marks}

    for p in PARTS:
        st.markdown(f"#### {p['part']} - {p['section']} (Max {p['max']} per item)")
        # Table header
        table_cols = st.columns([1, 8, 2])
        table_cols[0].markdown("**No.**")
        table_cols[1].markdown("**Assessment Item**")
        table_cols[2].markdown("**Marks**")
        for idx, text in enumerate(p['items'], start=1):
            row_cols = st.columns([1, 8, 2])
            row_cols[0].markdown(f"{idx}")
            row_cols[1].markdown(f"{text}")
            # Create unique key that includes part and section for global uniqueness
            key = f"score_{p['part']}_{p['section'].replace(' ', '_')}_{idx}"
            default = 0
            marks = row_cols[2].number_input(" ", min_value=0, max_value=p['max'], value=default, key=key)
            score_inputs.append({
                "part": p['part'],
                "section": p['section'],
                "item_no": idx,
                "item_text": text,
                "max_marks": p['max'],
                "marks_awarded": marks
            })

    # Observations and actions
    st.markdown("### 📝 Observations & Actions")
    obs_col1, obs_col2 = st.columns(2)
    with obs_col1:
        observations = st.text_area("General Observations", height=120, key="form_observations")
    with obs_col2:
        defects = st.text_area("Defects Identified", height=120, key="form_defects")
    corrective_actions = st.text_area("Corrective Actions Required", height=80, key="form_corrective_actions")

    # Submit button
    if st.button("💾 Submit Form", type="primary", key="form_submit_button"):
        # Basic validation
        if not employee_id:
            st.error("Employee ID is required")
            return
        if not employee_name:
            st.error("Employee name is required")
            return

        # validate each score
        for s in score_inputs:
            if s['marks_awarded'] < 0 or s['marks_awarded'] > s['max_marks']:
                st.error(f"Invalid marks for {s['part']} {s['section']} item {s['item_no']}")
                return

        # Ensure employee exists (create if missing)
        try:
            emp = get_employee(supabase, employee_id)
            if not emp:
                emp = create_employee(supabase, employee_id, employee_name)
                if not emp:
                    st.error("Failed to create employee record")
                    return
        except Exception as e:
            if 'JWT expired' in str(e):
                handle_jwt_expired()
            else:
                st.error(f"Error fetching/creating employee: {e}")
                return

        # Compute totals
        part_totals = {}
        overall = 0
        for p in PARTS:
            pts = sum([s['marks_awarded'] for s in score_inputs if s['part'] == p['part'] and s['section'] == p['section']])
            part_totals[f"{p['part']}_{p['section']}"] = pts
            overall += pts

        # Prepare metadata
        meta = {
            "employee_id": employee_id,
            "inspection_date": str(inspection_date),
            "submitted_at": datetime.utcnow().isoformat(),
            # Inspector information
            "inspected_by_user_id": st.session_state.get('user_id'),
            "inspected_by_name": st.session_state.get('user_name'),
            "inspected_by_role": st.session_state.get('user_role'),
            # Scores
            "part_a_total": sum([v for k, v in part_totals.items() if k.startswith('A_')]),
            "part_b_total": sum([v for k, v in part_totals.items() if k.startswith('B_')]),
            "part_c_total": sum([v for k, v in part_totals.items() if k.startswith('C_')]),
            "overall_total": overall,
            "observations": observations,
            "defects_identified": defects,
            "corrective_actions": corrective_actions,
            "ip_address": get_ip_address(),
            "device_info": get_device_info()
        }

        # Prepare scores payload
        scores_payload = []
        for s in score_inputs:
            scores_payload.append({
                "part": s['part'],
                "section": s['section'],
                "item_no": s['item_no'],
                "item_text": s['item_text'],
                "max_marks": s['max_marks'],
                "marks_awarded": s['marks_awarded']
            })

        try:
            with st.spinner("Saving inspection and scores..."):
                success, info = create_inspection_and_scores(supabase, meta, scores_payload)
        except Exception as e:
            if 'JWT expired' in str(e):
                handle_jwt_expired()
            else:
                st.error(f"Error saving inspection: {e}")
                return

        if success:
            st.success("Form saved successfully ✅")
            time.sleep(1.5)
            st.rerun()
        else:
            # Display user-friendly error messages
            if 'duplicate key value violates unique constraint' in str(info):
                st.warning("⚠️ **An inspection for this Employee and Date already exists.** Please select a different date to submit a new inspection.")
            else:
                st.warning("⚠️ **Failed to save the form.** Please check your entries and try again. If the problem persists, contact your administrator.")


if __name__ == '__main__':
    main()
