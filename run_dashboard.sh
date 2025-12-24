#!/bin/bash
# Clear Streamlit cache and run dashboard
echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit 2>/dev/null
echo "Starting Smart Finance Dashboard..."
streamlit run dashboards/streamlit_dashboard_multiuser.py --server.headless true
