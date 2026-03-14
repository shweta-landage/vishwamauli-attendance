import streamlit as st
import pandas as pd
from datetime import datetime
import os
import pytz

st.set_page_config(page_title="Vishwamauli Attendance", page_icon="🕉️", layout="wide")

# -------- TIMEZONE --------
ist = pytz.timezone("Asia/Kolkata")

# -------- SESSION --------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# -------- SIDEBAR --------
page = st.sidebar.selectbox(
    "Navigation",
    ["Worker Attendance", "Admin Dashboard"]
)

# ================= WORKER PAGE =================

if page == "Worker Attendance":

    st.title("🙏 Vishwamauli Attendance System")
    st.success("Vitthu Mauli Bless You 🌸")

    if os.path.exists("workers.csv"):
        workers_df = pd.read_csv("workers.csv")
        worker = st.selectbox("👤 Select Your Name", workers_df["Worker"])
    else:
        st.warning("No employees added yet.")
        st.stop()

    temple = st.selectbox(
        "🛕 Select Temple",
        ["-- Select Temple --", "Mauli Mandir", "Santoshi Mata Mandir", "Other"]
    )

    if temple == "-- Select Temple --":
        st.warning("Please select temple before marking attendance.")
        st.stop()

    action = st.radio("Attendance Type", ["🟢 Punch IN", "🔴 Punch OUT"])

    photo = st.camera_input("📸 Take Selfie")

    os.makedirs("images", exist_ok=True)

    if photo is not None:

        now = datetime.now(ist)

        date_today = now.strftime("%d-%m-%Y")
        time_now = now.strftime("%I:%M %p")
        file_time = now.strftime("%Y%m%d_%H%M%S")

        file_path = f"images/{file_time}.jpg"

        if os.path.exists("attendance.csv"):
            existing_df = pd.read_csv("attendance.csv")
        else:
            existing_df = pd.DataFrame(columns=["Worker","Temple","Date","Time","Action","Image"])

        duplicate = existing_df[
            (existing_df["Worker"] == worker) &
            (existing_df["Date"] == date_today) &
            (existing_df["Action"] == action)
        ]

        if not duplicate.empty:
            st.warning(f"{worker} already marked {action} today.")
            st.stop()

        with open(file_path, "wb") as f:
            f.write(photo.getbuffer())

        data = {
            "Worker": worker,
            "Temple": temple,
            "Date": date_today,
            "Time": time_now,
            "Action": action,
            "Image": file_path
        }

        df = pd.DataFrame([data])

        df.to_csv(
            "attendance.csv",
            mode="a",
            header=not os.path.exists("attendance.csv"),
            index=False
        )

        st.success("✅ Attendance Recorded Successfully 🙏")

    st.caption("🌼 Vishwamauli Attendance | Built with ❤️")


# ================= ADMIN DASHBOARD =================

if page == "Admin Dashboard":

    st.title("📊 Admin Dashboard")

    if not st.session_state.admin_logged:

        password = st.text_input("Enter Admin Password", type="password")

        if password == "vishwamauli123":
            st.session_state.admin_logged = True
            st.rerun()

        elif password != "":
            st.error("Incorrect Password")

    if st.session_state.admin_logged:

        if st.button("Logout"):
            st.session_state.admin_logged = False
            st.rerun()

        st.success("Admin Access Granted")

        st.divider()

        # -------- ADD EMPLOYEE --------

        st.subheader("➕ Add Employee")

        new_worker = st.text_input("Employee Name")

        if st.button("Add Employee"):

            if new_worker.strip() == "":
                st.warning("Employee name cannot be empty")

            else:

                if os.path.exists("workers.csv"):
                    workers_df = pd.read_csv("workers.csv")
                else:
                    workers_df = pd.DataFrame(columns=["Worker"])

                if new_worker not in workers_df["Worker"].values:

                    workers_df.loc[len(workers_df)] = new_worker
                    workers_df.to_csv("workers.csv", index=False)

                    st.success(f"{new_worker} added successfully!")

                else:
                    st.warning("Employee already exists")

        st.divider()

        # -------- DELETE EMPLOYEE --------

        if os.path.exists("workers.csv"):

            st.subheader("🗑 Delete Employee")

            workers_df = pd.read_csv("workers.csv")

            delete_worker = st.selectbox(
                "Select Employee to Remove",
                workers_df["Worker"]
            )

            if st.button("Delete Employee"):
                workers_df = workers_df[workers_df["Worker"] != delete_worker]
                workers_df.to_csv("workers.csv", index=False)
                st.success(f"{delete_worker} removed")

        st.divider()

        # -------- ADMIN MANUAL ATTENDANCE --------

        st.subheader("📝 Admin Manual Attendance")

        if os.path.exists("workers.csv"):

            workers_df = pd.read_csv("workers.csv")

            manual_worker = st.selectbox(
                "Select Worker",
                workers_df["Worker"],
                key="manual_worker"
            )

            manual_temple = st.selectbox(
                "Select Temple",
                ["Mauli Mandir", "Santoshi Mata Mandir", "Other"],
                key="manual_temple"
            )

            manual_action = st.radio(
                "Action",
                ["🟢 Punch IN", "🔴 Punch OUT"],
                key="manual_action"
            )

            if st.button("Mark Attendance"):

                now = datetime.now(ist)

                date_today = now.strftime("%d-%m-%Y")
                time_now = now.strftime("%I:%M %p")

                data = {
                    "Worker": manual_worker,
                    "Temple": manual_temple,
                    "Date": date_today,
                    "Time": time_now,
                    "Action": manual_action,
                    "Image": "ADMIN ENTRY"
                }

                df = pd.DataFrame([data])

                df.to_csv(
                    "attendance.csv",
                    mode="a",
                    header=not os.path.exists("attendance.csv"),
                    index=False
                )

                st.success(f"Attendance marked for {manual_worker}")

        st.divider()

        # -------- ATTENDANCE RECORDS --------

        if os.path.exists("attendance.csv"):

            df = pd.read_csv("attendance.csv")

            col1, col2, col3 = st.columns(3)

            col1.metric("Workers", df["Worker"].nunique())
            col2.metric("Temples", df["Temple"].nunique())
            col3.metric("Entries", len(df))

            st.divider()

            st.subheader("📋 Attendance Records")

            # small table for mobile
            df_display = df[["Worker","Temple","Date","Time","Action"]]

            st.dataframe(df_display, height=300)

            # -------- VIEW PHOTO --------

            st.subheader("📸 View Attendance Photo")

            record_index = st.number_input(
                "Enter row number",
                min_value=0,
                max_value=len(df)-1,
                step=1
            )

            if st.button("Show Photo"):

                image_path = df.loc[record_index, "Image"]

                if image_path == "ADMIN ENTRY":
                    st.info("Admin manual entry – no selfie available")

                elif os.path.exists(image_path):
                    st.image(image_path, width=300)

                else:
                    st.warning("Image not found")

            st.divider()

            # -------- DELETE ATTENDANCE --------

            st.subheader("🗑 Delete Attendance Record")

            row_delete = st.number_input(
                "Row number to delete",
                min_value=0,
                max_value=len(df)-1,
                step=1,
                key="delete_row"
            )

            if st.button("Delete Record"):

                df = df.drop(row_delete)
                df.to_csv("attendance.csv", index=False)

                st.success("Record deleted")

            st.divider()

            # -------- WORK HOURS --------

            st.subheader("⏱ Work Hours Summary")

            df["DateTime"] = pd.to_datetime(df["Date"] + " " + df["Time"])

            work_hours = []

            for worker in df["Worker"].unique():

                worker_data = df[df["Worker"] == worker]

                for date in worker_data["Date"].unique():

                    day_data = worker_data[worker_data["Date"] == date]

                    punch_in = day_data[day_data["Action"] == "🟢 Punch IN"]
                    punch_out = day_data[day_data["Action"] == "🔴 Punch OUT"]

                    if not punch_in.empty and not punch_out.empty:

                        in_time = punch_in.iloc[0]["DateTime"]
                        out_time = punch_out.iloc[0]["DateTime"]

                        seconds = (out_time - in_time).total_seconds()

                        hours = int(seconds // 3600)
                        minutes = int((seconds % 3600) // 60)

                        work_hours.append({
                            "Worker": worker,
                            "Date": date,
                            "Total Hours": f"{hours}h {minutes}m"
                        })

            if work_hours:
                st.dataframe(pd.DataFrame(work_hours))

            # -------- DOWNLOAD CSV --------

            with open("attendance.csv", "rb") as file:
                st.download_button(
                    label="⬇ Download Attendance",
                    data=file,
                    file_name="attendance.csv",
                    mime="text/csv"
                )

        else:
            st.info("No attendance records yet.")