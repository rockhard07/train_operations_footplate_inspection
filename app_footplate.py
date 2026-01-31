"""
Main entry point for Footplate Inspection System
Handles authentication and page navigation
"""

import streamlit as st
import sys
from datetime import datetime, timedelta
import pandas as pd
sys.path.insert(0, '.')
from auth import check_authentication, logout, show_user_info

st.set_page_config(page_title="Footplate Inspection System", page_icon="🚂", layout="wide")

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# If not authenticated, show login
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.markdown("""
        <style>
        .login-container { max-width: 400px; margin: 0 auto; }
        .login-header { text-align: center; font-size: 2rem; font-weight: 700; margin-bottom: 2rem; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-header'>🚂 Footplate Inspection System</div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h3>Login</h3></div>", unsafe_allow_html=True)
    
    try:
        from supabase import create_client
        SUPABASE_AVAILABLE = True
    except Exception:
        SUPABASE_AVAILABLE = False
        st.error("Supabase package not installed. Install with: pip install supabase")
        st.stop()
    
    @st.cache_resource
    def init_supabase():
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["key"]
            return create_client(url, key)
        except Exception as e:
            st.error(f"Failed to connect to Supabase: {e}")
            return None
    
    supabase = init_supabase()
    if not supabase:
        st.stop()
    
    # Login form
    email = st.text_input("Email Address", placeholder="user@example.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Login", type="primary", use_container_width=True):
        if not email or not password:
            st.warning("Please enter both email and password.")
        else:
            with st.spinner("Logging in..."):
                try:
                    # Authenticate with Supabase
                    response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    
                    # Get user role from users table
                    user_data = supabase.table("users").select("id, full_name, role").eq("id", response.user.id).limit(1).execute()
                    
                    if user_data and user_data.data:
                        user_info = user_data.data[0]
                        
                        # Store in session
                        st.session_state.authenticated = True
                        st.session_state.user_id = response.user.id
                        st.session_state.user_email = email
                        st.session_state.user_name = user_info.get('full_name', email)
                        st.session_state.user_role = user_info.get('role', 'manager')
                        st.session_state.access_token = response.session.access_token
                        st.session_state.supabase = supabase
                        
                        st.success(f"Welcome, {st.session_state.user_name}! 👋")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("User profile not found. Please contact your administrator.")
                except Exception as e:
                    error_msg = str(e)
                    if 'Invalid login credentials' in error_msg or 'invalid_credentials' in error_msg:
                        st.error("❌ Invalid email or password.")
                    else:
                        st.error("❌ Login failed. Please try again.")
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 0.9rem; color: #888;'>Contact your administrator if you don't have an account.</div>", unsafe_allow_html=True)

else:
    # User is authenticated - show main app
    show_user_info()
    
    user_role = st.session_state.get('user_role', 'manager').lower()
    
    # Sidebar navigation
    st.sidebar.markdown("# 🚂 Navigation")
    
    # Dashboard button - visible to all authenticated users
    if st.sidebar.button("📊 Dashboard", use_container_width=True, key="sidebar_dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()
    
    # Inspection Form button - visible to Manager, HOD, Admin
    if user_role in ['manager', 'hod', 'admin']:
        if st.sidebar.button("📝 Inspection Form", use_container_width=True, key="sidebar_inspection_form"):
            st.session_state.current_page = 'inspection_form'
            st.rerun()
    
    # Executive Dashboard button - visible to HOD, Admin only
    if user_role in ['hod', 'admin']:
        if st.sidebar.button("📈 Executive Dashboard", use_container_width=True, key="sidebar_executive_dashboard"):
            st.session_state.current_page = 'executive_dashboard'
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Role:** {user_role.capitalize()}")
    
    # Main content area
    st.markdown("# 🚂 Footplate Inspection System")
    st.markdown("---")
    
    # Render pages based on current_page
    if st.session_state.current_page == 'dashboard':
        if user_role in ['hod', 'admin']:
            st.markdown("""
            ## 📊 Executive Dashboard
            
            Welcome to the Footplate Inspection system. Use the sidebar navigation to access different sections.
            
            ### Available Features:
            - **Inspection Form**: Fill out new footplate inspection forms for employees
            - **Executive Dashboard**: View analytics and inspection reports (HOD only)
            
            ### Your Role: """ + user_role.capitalize())
        else:
            st.markdown("""
            ## 📊 Dashboard
            
            Welcome to the Footplate Inspection system. Use the sidebar navigation to access different sections.
            
            ### Available Features:
            - **Inspection Form**: Fill out new footplate inspection forms for employees
            - **Dashboard**: View analytics and inspection reports
            
            ### Your Role: """ + user_role.capitalize())
        
        # Add pending inspections table
        st.markdown("---")
        st.subheader("⏳ Employees with Pending Inspections (> 20 days)")
        
        try:
            # Get Supabase connection from session
            supabase = st.session_state.get('supabase')
            if not supabase:
                st.error("Database connection not available.")
            else:
                # Calculate the date from 20 days ago
                twenty_days_ago = (datetime.now() - timedelta(days=20)).date()
                
                # Query employees and their latest inspection dates
                employees_response = supabase.table("employees").select("employee_id, name, designation").execute()
                employees = {emp['employee_id']: emp for emp in employees_response.data}
                
                # Get all inspections to find latest inspection date per employee
                inspections_response = supabase.table("footplate_inspections").select("employee_id, inspection_date").order("inspection_date", desc=True).execute()
                
                # Build dictionary of latest inspection date per employee
                latest_inspection = {}
                for inspection in inspections_response.data:
                    emp_id = inspection['employee_id']
                    if emp_id not in latest_inspection:
                        latest_inspection[emp_id] = inspection['inspection_date']
                
                # Find employees with pending inspections > 20 days
                pending_employees = []
                for emp_id, emp_data in employees.items():
                    if emp_id not in latest_inspection:
                        # No inspection at all
                        pending_employees.append({
                            'Employee ID': emp_id,
                            'Employee Name': emp_data['name'],
                            'Designation': emp_data['designation'],
                            'Inspection Pending Since': 'Never inspected'
                        })
                    else:
                        # Check if latest inspection is older than 20 days
                        last_inspection_date = datetime.strptime(latest_inspection[emp_id], '%Y-%m-%d').date()
                        if last_inspection_date <= twenty_days_ago:
                            pending_employees.append({
                                'Employee ID': emp_id,
                                'Employee Name': emp_data['name'],
                                'Designation': emp_data['designation'],
                                'Inspection Pending Since': last_inspection_date.strftime('%Y-%m-%d')
                            })
                
                # Display the table
                if pending_employees:
                    df_pending = pd.DataFrame(pending_employees)
                    st.dataframe(df_pending, use_container_width=True, hide_index=True)
                    st.info(f"📊 Total employees with pending inspections (> 20 days): {len(pending_employees)}")
                else:
                    st.success("✅ No employees with pending inspections beyond 20 days!")
                    
        except Exception as e:
            st.error(f"Error retrieving pending inspections: {str(e)}")
        
        
    elif st.session_state.current_page == 'inspection_form':
        st.markdown("## 📝 Footplate Inspection Form")
        
        # Import and run the form code
        try:
            from _footplate_inspection_form import main as inspection_main
            inspection_main()
        except Exception as e:
            st.error(f"Error loading inspection form: {e}")
    
    elif st.session_state.current_page == 'executive_dashboard':
        if user_role not in ['hod', 'admin']:
            st.error("Access Denied. This page is only available for HOD and Admin.")
        else:
            st.markdown("## 📊 Executive Dashboard")
            
            # Import and run the executive dashboard code
            try:
                from _footplate_executive_dashboard import main as exec_dash_main
                exec_dash_main()
            except Exception as e:
                st.error(f"Error loading executive dashboard: {e}")
