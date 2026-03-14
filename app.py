import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Vishwamauli Attendance", page_icon="🕉️", layout="wide")

# ---------------- SESSION ----------------

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# ---------------- SIDEBAR ----------------

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
        ["-- Select Temple --", "Mauli Mandir", "Santoshi Mata Mandir"]
    )

    if temple == "-- Select Temple --":
        st.warning("Please select temple before marking attendance.")
        st.stop()

    action = st.radio("Attendance Type", ["🟢 Punch IN", "🔴 Punch OUT"])

    photo = st.camera_input("📸 Take Selfie")

    os.makedirs("images", exist_ok=True)

    if photo is not None:

        now = datetime.now()

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

        st.success("Admin Access Granted")

        # -------- Add Employee --------

        st.subheader("➕ Add New Employee")

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

        # -------- Attendance Records --------

        if os.path.exists("attendance.csv"):

            df = pd.read_csv("attendance.csv")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Workers", df["Worker"].nunique())

            with col2:
                st.metric("Temples", df["Temple"].nunique())

            with col3:
                st.metric("Entries", len(df))

            st.divider()

            st.subheader("📋 Attendance Records")

            # Header row

            h1, h2, h3, h4, h5, h6 = st.columns([1.5,2,1.5,1.5,1.5,1])

            h1.markdown("**Worker**")
            h2.markdown("**Temple**")
            h3.markdown("**Date**")
            h4.markdown("**Time**")
            h5.markdown("**Action**")
            h6.markdown("**Image**")

            # Rows

            for i, row in df.iterrows():

                col1, col2, col3, col4, col5, col6 = st.columns([1.5,2,1.5,1.5,1.5,1])

                col1.write(row["Worker"])
                col2.write(row["Temple"])
                col3.write(row["Date"])
                col4.write(row["Time"])
                col5.write(row["Action"])

                if col6.button("View", key=f"img{i}"):

                    image_path = row["Image"]

                    if os.path.exists(image_path):
                        st.image(image_path, width=350)

            st.divider()

            # -------- Work Hours --------

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
                st.dataframe(pd.DataFrame(work_hours), use_container_width=True)

            # Download CSV

            with open("attendance.csv", "rb") as file:
                st.download_button(
                    label="⬇ Download Attendance",
                    data=file,
                    file_name="attendance.csv",
                    mime="text/csv"
                )

        else:
            st.info("No attendance records yet.")