"""
Authentication and authorization utilities
"""

import streamlit as st
from typing import List, Optional


def check_authentication() -> bool:
    """
    Check if user is authenticated
    Returns True if authenticated, False otherwise
    """
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    return st.session_state.authenticated


def check_role_access(allowed_roles: List[str]) -> bool:
    """
    Check if user's role has access to allowed_roles
    
    Args:
        allowed_roles: List of allowed roles (e.g., ['manager', 'hod', 'admin'])
    
    Returns:
        True if user's role is in allowed_roles, False otherwise
    """
    if not check_authentication():
        return False
    
    user_role = st.session_state.get('user_role', '').lower()
    return user_role in [role.lower() for role in allowed_roles]


def logout():
    """
    Logout user by clearing session state
    """
    session_vars_to_clear = [
        'authenticated', 'user_id', 'user_email', 'user_name',
        'user_role', 'access_token', 'supabase', 'current_page'
    ]
    
    for var in session_vars_to_clear:
        if var in st.session_state:
            del st.session_state[var]
    
    st.rerun()


def show_user_info():
    """
    Display user information and logout button in sidebar
    """
    if check_authentication():
        user_name = st.session_state.get('user_name', 'User')
        user_email = st.session_state.get('user_email', 'N/A')
        
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"### 👤 {user_name}")
            st.caption(user_email)
            
            if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout_button"):
                logout()


def require_authentication():
    """
    Decorator/wrapper to ensure user is authenticated
    Used in pages that require authentication
    """
    if not check_authentication():
        st.error("❌ You must be logged in to access this page.")
        st.info("Please return to the home page and log in.")
        st.stop()


def require_role(allowed_roles: List[str]):
    """
    Decorator/wrapper to ensure user has required role
    
    Args:
        allowed_roles: List of allowed roles
    """
    if not check_role_access(allowed_roles):
        user_role = st.session_state.get('user_role', 'unknown')
        st.error(f"❌ Access Denied. Your role ({user_role}) does not have permission to access this page.")
        st.info(f"This page is only accessible to: {', '.join(allowed_roles)}")
        st.stop()
