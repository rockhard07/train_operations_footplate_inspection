"""
Executive Dashboard - Analytics for HOD and Admin
Shows inspector performance, inspection trends, and detailed employee analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta


def main():
    """Main function for executive dashboard"""
    
    # Check authentication and role
    from auth import check_authentication, check_role_access
    
    if not check_authentication():
        st.error("❌ Please log in to access this dashboard.")
        st.stop()
    
    if not check_role_access(['hod', 'admin']):
        st.error("❌ You do not have permission to access this dashboard.")
        st.stop()
    
    # Get Supabase client
    supabase = st.session_state.get('supabase')
    if not supabase:
        st.error("❌ Database connection failed.")
        st.stop()
    
    # Tab selection
    tab1, tab2, tab3 = st.tabs(["📊 Summary", "👥 Inspector Performance", "📈 Employee Analysis"])
    
    with tab1:
        st.markdown("## Executive Summary")
        
        try:
            # Get all inspections
            all_inspections = supabase.table("footplate_inspections").select("*").execute()
            inspections_df = pd.DataFrame(all_inspections.data) if all_inspections.data else pd.DataFrame()
            
            if not inspections_df.empty:
                # Summary metrics
                total_inspections = len(inspections_df)
                
                # This month
                today = datetime.now()
                current_month_start = datetime(today.year, today.month, 1)
                inspections_df['inspection_date'] = pd.to_datetime(inspections_df['inspection_date'])
                this_month = inspections_df[inspections_df['inspection_date'] >= current_month_start]
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Inspections", total_inspections)
                
                with col2:
                    st.metric("This Month", len(this_month))
                
                with col3:
                    avg_score = inspections_df['overall_total'].mean() if 'overall_total' in inspections_df else 0
                    st.metric("Average Score", f"{avg_score:.1f}")
                
                st.markdown("---")
                
                # Recent inspections
                st.markdown("### 📋 Latest Inspections")
                
                if not inspections_df.empty:
                    latest_inspections = inspections_df.sort_values('inspection_date', ascending=False).head(10)
                    
                    display_df = latest_inspections[['employee_id', 'inspection_date', 'inspected_by_name', 'overall_total']].copy()
                    display_df.columns = ['Employee ID', 'Date', 'Inspector', 'Total Score']
                    display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
                    
                    st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No inspections found in the system.")
        
        except Exception as e:
            st.error(f"Error loading summary: {e}")
    
    with tab2:
        st.markdown("## 👥 Inspector Performance")
        
        try:
            # Get inspector statistics
            all_inspections = supabase.table("footplate_inspections").select("*").execute()
            inspections_df = pd.DataFrame(all_inspections.data) if all_inspections.data else pd.DataFrame()
            
            if not inspections_df.empty:
                inspections_df['inspection_date'] = pd.to_datetime(inspections_df['inspection_date'])
                
                # Last 30 days
                thirty_days_ago = datetime.now() - timedelta(days=30)
                recent = inspections_df[inspections_df['inspection_date'] >= thirty_days_ago]
                
                if not recent.empty:
                    # Group by inspector
                    inspector_stats = recent.groupby('inspected_by_name').agg({
                        'id': 'count',
                        'overall_total': ['mean', 'min', 'max']
                    }).round(2)
                    
                    inspector_stats.columns = ['Inspections', 'Avg Score', 'Min Score', 'Max Score']
                    inspector_stats = inspector_stats.sort_values('Inspections', ascending=False)
                    
                    st.dataframe(inspector_stats, use_container_width=True)
                else:
                    st.info("No inspections in the last 30 days.")
            else:
                st.info("No inspections found in the system.")
        
        except Exception as e:
            st.error(f"Error loading inspector performance: {e}")
    
    with tab3:
        st.markdown("## 📈 Employee Analysis")
        
        try:
            # Get employee list
            employees_response = supabase.table("employees").select("employee_id, name").execute()
            employees_list = {emp['name']: emp['employee_id'] for emp in employees_response.data} if employees_response.data else {}
            
            if employees_list:
                # Employee selector
                selected_employee_name = st.selectbox(
                    "Select Employee",
                    options=list(employees_list.keys()),
                    key="exec_employee_id_input"
                )
                
                selected_employee_id = employees_list[selected_employee_name]
                
                # Date range picker
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30), key="exec_start_date")
                with col2:
                    end_date = st.date_input("End Date", value=datetime.now(), key="exec_end_date")
                
                # Get inspections for this employee
                all_inspections = supabase.table("footplate_inspections").select("*").eq("employee_id", selected_employee_id).execute()
                inspections_df = pd.DataFrame(all_inspections.data) if all_inspections.data else pd.DataFrame()
                
                if not inspections_df.empty:
                    inspections_df['inspection_date'] = pd.to_datetime(inspections_df['inspection_date'])
                    
                    # Filter by date range
                    filtered = inspections_df[
                        (inspections_df['inspection_date'] >= pd.to_datetime(start_date)) &
                        (inspections_df['inspection_date'] <= pd.to_datetime(end_date))
                    ]
                    
                    if not filtered.empty:
                        # Statistics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Inspections", len(filtered))
                        
                        with col2:
                            avg_score = filtered['overall_total'].mean()
                            st.metric("Average Score", f"{avg_score:.1f}")
                        
                        with col3:
                            last_inspection = filtered.sort_values('inspection_date', ascending=False).iloc[0]
                            st.metric("Last Inspection", last_inspection['inspection_date'].strftime('%Y-%m-%d'))
                        
                        st.markdown("---")
                        
                        # Inspection history
                        st.markdown("### Inspection History")
                        
                        display_df = filtered[['inspection_date', 'part_a_total', 'part_b_total', 'overall_total']].copy()
                        display_df.columns = ['Date', 'Part A', 'Part B', 'Total']
                        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                        display_df = display_df.sort_values('Date', ascending=False)
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                        # Line chart of scores over time
                        if not filtered.empty:
                            chart_data = filtered[['inspection_date', 'overall_total']].sort_values('inspection_date')
                            chart_data.columns = ['Date', 'Score']
                            chart_data = chart_data.set_index('Date')
                            
                            st.line_chart(chart_data)
                    else:
                        st.info("No inspections found for this employee in the selected date range.")
                else:
                    st.info("No inspection history for this employee.")
            else:
                st.info("No employees found in the system.")
        
        except Exception as e:
            st.error(f"Error loading employee analysis: {e}")


if __name__ == "__main__":
    main()
