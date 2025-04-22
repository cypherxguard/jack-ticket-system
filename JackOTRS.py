import streamlit as st
import pandas as pd
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from io import BytesIO
import hashlib


st.set_page_config(
    page_title="Ticket Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------
# Auth setup
# ----------------------------------------
USERS = {
    "jack": "admin123",
    "admin": "securepass"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Session setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Login UI (only called after set_page_config)
def login():
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Logout logic
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("You have been logged out.")


if not st.session_state.logged_in:
    st.title("🔐 Login")
    login()
    st.stop()
else:
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            logout()
            st.stop()

# -------------------------------------------------------------
# Custom CSS & FontAwesome for Icons
# -------------------------------------------------------------
st.markdown("""
    <style>
    /* Import a modern font */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Open Sans', sans-serif;
    }

    /* Override default backgrounds and text colors */
    body, .reportview-container, .main {
        background-color: #f8f9fa !important;
        color: #343a40;
    }

    /* === SIDEBAR STYLING === */
    .css-12oz5g7 {
        background-color: #343a40 !important; /* Dark background */
    }
    .css-1d391kg {
        padding: 1rem; /* Spacing inside the sidebar */
    }

    /* Profile-like section with a gradient background */
    .sidebar-profile {
        background: linear-gradient(135deg, #4b4b4b, #2f2f2f);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .sidebar-profile i {
        font-size: 60px;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .sidebar-profile h2 {
        color: #ffffff;
        margin: 0;
        font-size: 1.3rem;
    }
    .sidebar-profile p {
        color: #cccccc;
        font-size: 0.9rem;
        margin-top: 0.2rem;
    }

    /* Sidebar radio button styling */
    .stRadio > label {
        display: none; /* Hide default "Go to" label */
    }
    div[data-baseweb="radio"] > div {
        margin-bottom: 10px !important;
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
    div[data-baseweb="radio"] label {
        color: #ffffff;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.4rem 0.6rem;
        width: 100%;
        display: inline-block;
        border-radius: 8px;
    }
    div[data-baseweb="radio"] input:checked ~ div label {
        background-color: #007bff;
        color: #ffffff;
    }
    div[data-baseweb="radio"] label:hover {
        background-color: #555555;
        cursor: pointer;
    }

    /* === HEADINGS === */
    h1, h2, h3, h4, h5, h6 {
        color: #007bff;
        margin-top: 0;
    }

    /* === BUTTONS === */
    .stButton button {
        background-color: #007bff !important;
        color: #ffffff !important;
        border: none;
        border-radius: 4px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #0056b3 !important;
    }

    /* === DATAFRAME STYLING === */
    .stDataFrame {
        border: 1px solid #dee2e6 !important;
        border-radius: 4px;
    }

    /* === HERO SECTION === */
    .hero {
        background-color: #343a40;
        padding: 3rem;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero h1 {
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .hero p {
        color: #dddddd;
        font-size: 1.1rem;
        max-width: 600px;
        margin: 0 auto;
    }

    /* === FEATURE ICONS === */
    .feature-box {
        text-align: center;
        padding: 1rem;
    }
    .feature-box i {
        font-size: 40px;
        color: #007bff;
        margin-bottom: 0.5rem;
    }
    .feature-box h4 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    </style>

    <!-- Load FontAwesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Database Setup (SQLite)
# -------------------------------------------------------------
conn = sqlite3.connect('ticket_system.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        last_name TEXT NOT NULL,
        court_date TEXT,
        citation_date TEXT,
        contact_date TEXT,
        ticket_type TEXT,
        county TEXT,
        court TEXT,
        notes TEXT,
        source TEXT,
        other TEXT,
        ticket_image BLOB
    )
''')
conn.commit()

def insert_ticket(data):
    """Insert a new ticket into the tickets table."""
    cursor.execute('''
        INSERT INTO tickets
        (first_name, middle_name, last_name, court_date, citation_date, contact_date,
         ticket_type, county, court, notes, source, other, ticket_image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()

def send_email_notification(smtp_server, smtp_port, smtp_username, smtp_password, recipient, subject, message):
    """Send an email using the provided SMTP settings."""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {e}"

def export_to_excel():
    """Export tickets from the database to an Excel file in memory."""
    df = pd.read_sql_query("SELECT * FROM tickets", conn)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Tickets")
    processed_data = output.getvalue()
    return processed_data

# -------------------------------------------------------------
# Enhanced Sidebar with a Profile-Like Section
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-profile">
        <i class="fas fa-user-tie"></i>
        <h2>Jack</h2>
        <p>Traffic Tickets Admin</p>
    </div>
    """, unsafe_allow_html=True)

    menu_options = {
        "🏠  Dashboard": "Dashboard",
        "➕  Add Ticket": "Add Ticket",
        "📁  Upload Tickets": "Upload Tickets",
        "📋  View Tickets": "View Tickets",
        "📧  Send Notification": "Send Notification"
    }
    menu_choice = st.radio("", list(menu_options.keys()))
    menu = menu_options[menu_choice]

# -------------------------------------------------------------
# Dashboard (Landing Page)
# -------------------------------------------------------------
if menu == "Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Ticket Management System</h1>
        <p>Your all-in-one solution for managing traffic tickets with ease and efficiency.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-box">
            <i class="fas fa-file-upload"></i>
            <h4>Bulk Upload</h4>
            <p>Upload Excel files to handle multiple tickets at once.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-box">
            <i class="fas fa-user-edit"></i>
            <h4>Manual Entry</h4>
            <p>Enter ticket details individually with a clean, user-friendly form.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-box">
            <i class="fas fa-bell"></i>
            <h4>Notifications</h4>
            <p>Stay informed with email alerts for important milestones.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("Get Started")
    st.write("""
        - **Add Ticket:** Enter ticket details one by one.  
        - **Upload Tickets:** Bulk import from a .xlsx file.  
        - **View Tickets:** Review, delete, and export stored tickets.  
        - **Send Notification:** Email milestone updates or reminders.

        Use the sidebar on the left to navigate between these sections.
    """)

# -------------------------------------------------------------
# Add Ticket (Manual Entry)
# -------------------------------------------------------------
elif menu == "Add Ticket":
    st.title("Add a New Ticket")
    st.write("Fill out the form below with the ticket details.")
    
    with st.form("manual_ticket_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            first_name = st.text_input("First Name", max_chars=50)
            middle_name = st.text_input("Middle Name", max_chars=50)
            last_name = st.text_input("Last Name", max_chars=50)
        
        with col2:
            court_date = st.date_input("Court Date", value=date.today())
            citation_date = st.date_input("Citation Date", value=date.today())
            contact_date = st.date_input("Contact Date", value=date.today())
        
        with col3:
            ticket_type = st.text_input("Ticket Type", max_chars=50)
            county = st.text_input("County", max_chars=50)
            court = st.text_input("Court", max_chars=100)
        
        notes = st.text_area("Notes", height=80)
        source = st.text_input("Source", max_chars=100)
        other = st.text_input("Other", max_chars=100)

        # Image upload
        uploaded_image = st.file_uploader("Upload Ticket Image", type=["jpg", "png", "jpeg"])
        
        submitted = st.form_submit_button("Submit Ticket")
        if submitted:
            if not first_name or not last_name:
                st.error("First Name and Last Name are required fields.")
            else:
                if uploaded_image is not None:
                    img_data = uploaded_image.read()
                else:
                    img_data = None
                
                data = (
                    first_name.strip(), 
                    middle_name.strip(), 
                    last_name.strip(), 
                    court_date.isoformat(), 
                    citation_date.isoformat(), 
                    contact_date.isoformat(),
                    ticket_type.strip(), 
                    county.strip(), 
                    court.strip(), 
                    notes.strip(), 
                    source.strip(), 
                    other.strip(),
                    img_data  # Store the image as binary data
                )
                insert_ticket(data)
                st.success("Ticket added successfully!")

# -------------------------------------------------------------
# Bulk Upload Tickets  (NEW: accepts any Excel format "as‑is")
# -------------------------------------------------------------
elif menu == "Upload Tickets":
    st.title("Bulk Upload (Any Excel Format)")
    st.write("Upload any .xlsx file – columns will be stored exactly as‑is.")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    if uploaded_file:
        try:
            # Load Excel – treat first row as header if present, else generic headers
            df = pd.read_excel(uploaded_file, header=0)
            if df.columns.tolist()[0].startswith("Unnamed"):
                # No headers present – generate Column 1, Column 2, ...
                df.columns = [f"Column {i+1}" for i in range(len(df.columns))]

            # Preview for Jack
            st.write("**Preview of Uploaded Data**")
            st.dataframe(df)

            if st.button("Save Data"):
                # Save raw data to a flexible table
                df.to_sql("raw_uploads", conn, if_exists="append", index=False)
                st.success("File imported and saved successfully!")
        except Exception as e:
            st.error(f"Error processing file: {e}")

# -------------------------------------------------------------
# View Data (Tickets or Raw Uploads)
# -------------------------------------------------------------
elif menu == "View Tickets":
    st.title("View Stored Data")

    # Choose which table to display
    table_choice = st.radio(
        "Select dataset",
        ["Structured Tickets", "Raw Uploads"],
        horizontal=True
    )

    table_name = "tickets" if table_choice == "Structured Tickets" else "raw_uploads"

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        st.dataframe(df)

        # Export to Excel for whichever table is being viewed
        if not df.empty:
            excel_data = df.to_excel(index=False, engine="xlsxwriter")
            st.download_button(
                label="Export to Excel",
                data=excel_data,
                file_name=f"{table_name}_export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # Delete only for tickets table (optional)
        if table_name == "tickets" and not df.empty:
            st.write("---")
            st.subheader("Delete a Structured Ticket")
            ticket_options = [(row["id"], f"ID {row['id']}: {row['first_name']} {row['last_name']}") 
                              for _, row in df.iterrows()]
            ticket_dict = dict(ticket_options)
            ticket_ids = [t[0] for t in ticket_options]
            selected_ticket = st.selectbox("Select to delete", ticket_ids, format_func=lambda x: ticket_dict[x])
            if st.button("Delete Ticket"):
                cursor.execute("DELETE FROM tickets WHERE id = ?", (selected_ticket,))
                conn.commit()
                st.success(f"Ticket {selected_ticket} deleted successfully!")
                st.experimental_rerun()
        elif table_name == "raw_uploads" and df.empty:
            st.info("No raw uploads yet.")
        elif table_name == "tickets" and df.empty:
            st.info("No structured tickets yet.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")

# -------------------------------------------------------------
# Send Email Notification
# -------------------------------------------------------------
elif menu == "Send Notification":
    st.title("Send Email Notification")
    st.write("Fill in the SMTP settings and email details below to send a notification.")
    
    with st.form("notification_form"):
        smtp_server = st.text_input("SMTP Server", value="smtp.example.com")
        smtp_port = st.number_input("SMTP Port", value=587, step=1)
        smtp_username = st.text_input("SMTP Username", value="your_username")
        smtp_password = st.text_input("SMTP Password", type="password", value="your_password")
        recipient = st.text_input("Recipient Email", value="recipient@example.com")
        subject = st.text_input("Email Subject", value="Ticket Milestone Notification")
        message = st.text_area("Email Message", height=100, value="A milestone has been reached in your ticket system.")
        
        submitted = st.form_submit_button("Send Notification")
        if submitted:
            success, result_message = send_email_notification(
                smtp_server, smtp_port, smtp_username, smtp_password, 
                recipient, subject, message
            )
            if success:
                st.success(result_message)
            else:
                st.error(result_message)

# -------------------------------------------------------------
# Footer
# -------------------------------------------------------------
st.sidebar.info("© 2025 Ticket Management System - Jack")
