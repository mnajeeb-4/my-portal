import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ---------- Constants ----------
FILE_NAME = "students.json"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"
SUBJECTS = ["English", "Urdu", "Math", "Science", "Sindhi", "Islamiyat", "Social Studies"]
TOTAL_MARKS = 700

# ---------- Helper Functions ----------
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                return json.load(file)
        except:
            return {}
    return {}

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

def calculate_grade(percentage):
    if percentage >= 80: return "A-1"
    elif percentage >= 70: return "A"
    elif percentage >= 60: return "B"
    elif percentage >= 50: return "C"
    else: return "Fail"

# ---------- UI Config ----------
st.set_page_config(page_title="Student Management System", layout="wide")

# Sidebar Navigation (Wahi options jo aapke main menu mein thay)
st.sidebar.title("SMS Navigation")
choice = st.sidebar.radio("Select Option:", ["Main Menu", "Admin Login", "Student Login"])

data = load_data()

# --- MAIN MENU ---
if choice == "Main Menu":
    st.title("🎓 Student Management System")
    st.info("Welcome! Please select your portal from the sidebar to continue.")
    st.write("Current System Status: Online ✅")

# --- ADMIN SECTION ---
elif choice == "Admin Login":
    st.title("🔐 Admin Panel")
    
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("Login"):
            if user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
    else:
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_auth": False}))
        
        # Admin Features
        admin_opt = st.selectbox("Admin Actions", ["Add Student", "View All Records", "Update Marks", "Export CSV"])
        
        if admin_opt == "Add Student":
            st.subheader("Add New Student")
            with st.form("add_form"):
                roll = st.text_input("Roll Number")
                name = st.text_input("Student Name")
                class_name = st.text_input("Class")
                st.write("Enter Marks (0-100):")
                marks = {}
                cols = st.columns(2)
                for i, sub in enumerate(SUBJECTS):
                    marks[sub] = cols[i%2].number_input(sub, 0, 100)
                
                if st.form_submit_button("Save Student"):
                    if roll in data:
                        st.warning("Student already exists.")
                    else:
                        data[roll] = {"name": name, "class": class_name, "marks": marks, "date": str(datetime.now().date())}
                        save_data(data)
                        st.success("Student added successfully!")

        elif admin_opt == "View All Records":
            st.subheader("All Student Records")
            if data:
                view_list = []
                for r, info in data.items():
                    total = sum(info['marks'].values())
                    view_list.append({"Roll": r, "Name": info['name'], "Class": info['class'], "Total": total})
                st.table(pd.DataFrame(view_list))
            else:
                st.info("No records found.")

        elif admin_opt == "Update Marks":
            st.subheader("Update Student Marks")
            u_roll = st.text_input("Enter Roll No to Update")
            if u_roll in data:
                with st.form("update_form"):
                    st.write(f"Updating marks for: {data[u_roll]['name']}")
                    new_marks = {}
                    for sub in SUBJECTS:
                        new_marks[sub] = st.number_input(sub, 0, 100, value=data[u_roll]['marks'].get(sub, 0))
                    if st.form_submit_button("Update"):
                        data[u_roll]['marks'] = new_marks
                        save_data(data)
                        st.success("Marks updated!")
            else:
                st.error("Roll number not found.")

        elif admin_opt == "Export CSV":
            st.subheader("Export to CSV")
            if data:
                export_list = []
                for r, info in data.items():
                    m = info['marks']
                    t = sum(m.values())
                    p = (t/TOTAL_MARKS)*100
                    row = {"Roll": r, "Name": info['name'], "Class": info['class']}
                    row.update(m)
                    row.update({"Total": t, "Percentage": round(p, 2), "Grade": calculate_grade(p)})
                    export_list.append(row)
                df_csv = pd.DataFrame(export_list)
                csv_data = df_csv.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV Report", data=csv_data, file_name="students_result.csv")

# --- STUDENT SECTION ---
elif choice == "Student Login":
    st.title("👨‍🎓 Student Result Portal")
    s_roll = st.text_input("Enter your Roll Number")
    if st.button("Get Result"):
        if s_roll in data:
            info = data[s_roll]
            st.header(f"Result for: {info['name']}")
            st.write(f"Class: {info['class']}")
            
            # Show Marks Table
            df_marks = pd.DataFrame(list(info['marks'].items()), columns=["Subject", "Obtained"])
            st.table(df_marks)
            
            total = sum(info['marks'].values())
            perc = (total/TOTAL_MARKS)*100
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Marks", f"{total} / {TOTAL_MARKS}")
            c2.metric("Percentage", f"{round(perc, 2)}%")
            c3.metric("Grade", calculate_grade(perc))
        else:
            st.error("Invalid Roll Number.")
