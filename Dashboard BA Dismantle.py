import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth

# ===============================
# KONFIGURASI LOGIN (fixed - hashed password)
# ===============================
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": "$2b$12$uL8kj4e1KTSUs1XMrKOd4.L9/EgYe12tw7UeRDwq7x6ZIXn7iH14C"  # hashed admin123
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "ba_dashboard",        # cookie name
    "abcdef123456",        # signature key
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", location="sidebar")

# ===============================
# HANDLE LOGIN STATUS
# ===============================
if authentication_status is False:
    st.error("Username atau password salah.")
elif authentication_status is None:
    st.warning("Silakan masukkan username dan password.")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Selamat datang, {name} 👋")

    # ===============================
    # DASHBOARD MULAI DI SINI
    # ===============================
    st.set_page_config(page_title="Dashboard BA Dismantle", layout="wide")
    st.title("📊 Dashboard Monitoring Assessment BA Dismantle")

    uploaded_file = st.file_uploader("📂 Upload file Excel (sheet: DismantlePerangkat)", type=["xlsx"])

    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            if "DismantlePerangkat" in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name="DismantlePerangkat")

                # Validasi kolom
                required_columns = ["SiteID", "SiteName", "Accuracy", "Detail"]
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    st.error(f"❗ Kolom berikut tidak ditemukan: {', '.join(missing_cols)}")
                    st.stop()

                # Hitung status
                total_docs = len(df)
                comply_count = (df["Accuracy"] == "Comply").sum()
                not_comply_count = (df["Accuracy"] == "Not Comply").sum()
                not_yet_assess_count = (df["Accuracy"] == "Not Yet Assess").sum()

                # Tampilan metric
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📄 Total Dokumen", total_docs)
                col2.metric("✅ Comply", comply_count)
                col3.metric("❌ Not Comply", not_comply_count)
                col4.metric("⏳ Not Yet Assess", not_yet_assess_count)

                # Pie chart
                st.subheader("📈 Distribusi Status Accuracy")
                status_counts = df["Accuracy"].value_counts()
                fig, ax = plt.subplots()
                ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)

                # Detail Not Comply / Not Yet Assess
                st.subheader("🔍 Detail Remarks (Not Comply / Not Yet Assess)")
                filtered_df = df[df["Accuracy"].isin(["Not Comply", "Not Yet Assess"])]
                st.dataframe(filtered_df[["SiteID", "SiteName", "Accuracy", "Detail"]], use_container_width=True)
            else:
                st.error("❗ Sheet 'DismantlePerangkat' tidak ditemukan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
