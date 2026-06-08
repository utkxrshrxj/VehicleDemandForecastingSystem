import streamlit as st

def apply_custom_css():
    """Applies a professional corporate CSS theme to Streamlit."""
    st.markdown("""
        <style>
        .main .block-container {
            max-width: 1600px;
            padding-top: 2rem;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2B3674 !important;
            font-family: 'Inter', sans-serif;
        }
        /* General text color - exclude multiselect tags and buttons */
        .stMarkdown p, .stMarkdown span,
        .stText, label, .stSidebar label,
        [data-testid="stSidebarNav"] span {
            color: #2B3674;
        }
        /* Multiselect selected chip: keep white text on purple background */
        [data-baseweb="tag"] span,
        [data-baseweb="tag"] {
            color: #ffffff !important;
        }
        /* Sidebar multiselect dropdown options */
        [data-baseweb="select"] [data-baseweb="option"] {
            color: #2B3674 !important;
        }
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0px 4px 12px rgba(112, 144, 176, 0.08);
            border-left: 5px solid #4318FF;
            text-align: center;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            color: #2B3674 !important;
            margin: 10px 0 0 0;
        }
        .metric-label {
            font-size: 14px;
            color: #A3AED0 !important;
            margin: 0;
            text-transform: uppercase;
            font-weight: 600;
        }
        .btn-download {
            display: inline-block;
            background-color: #4318FF;
            color: white !important;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 10px;
        }
        .btn-download:hover {
            background-color: #3965FF;
        }
        </style>
    """, unsafe_allow_html=True)
