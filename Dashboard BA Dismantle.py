import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth

# ===============================
# KONFIGURASI LOGIN
# ===============================
# Buat kredensial user login
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": stauth.Hasher(["admin123"]).generate()[0]
        },
        "olivia": {
            "name": "Olivia",
            "password": stauth.Hasher(["olivia456"]).generate()[0]
        }
    }
}

# Setup autentikasi
authenticator = stauth.Authenticate(
    credentials,
    "ba_dashboard",         # Cookie name (bebas)
    "abcdef123456",         # Signature key (bebas, bisa UUID)
    cookie_expiry_days=1
)

# Form login
name, authentication_status, username = authenticator.login("Login", "main")

# ===============================
# HANDLE STATUS LOGIN
# ===============================
if authentication_status is False:
    st.error("Username atau password salah.")
elif authentication_status is None:
    st.warning("Silakan masukkan username dan password.")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Selamat datang, {name} 👋")

    # ===============================
    # DASHBOARD STARTS HERE
    # ===============================
    st.set_page_config(page_title="Dashboard BA Dismantle", layout="wide")
    st.title("📊 Dashboard Monitoring Assessment BA Dismantle")

    # Upload file Excel
    uploaded_file = st.file_uploader("📂 Upload file Excel", type=["xlsx"])

    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            if "DismantlePerangkat" in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name="DismantlePerangkat")

                # Validasi kolom
                if "Accuracy" in df.columns and "Detail" in df.columns:
                    # Hitung status dokumen
                    total_docs = len(df)
                    comply_count = (df["Accuracy"] == "Comply").sum()
                    not_comply_count = (df["Accuracy"] == "Not Comply").sum()
                    not_yet_assess_count = (df["Accuracy"] == "Not Yet Assess").sum()

                    # Tampilkan metric summary
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("📄 Total Dokumen", total_docs)
                    col2.metric("✅ Comply", comply_count)
                    col3.metric("❌ Not Comply", not_comply_count)
                    col4.metric("⏳ Not Yet Assess", not_yet_assess_count)

                    # Pie chart distribusi
                    st.subheader("📈 Distribusi Status Accuracy")
                    status_counts = df["Accuracy"].value_counts()
                    fig, ax = plt.subplots()
                    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')
                    st.pyplot(fig)

                    # Detail remarks untuk Not Comply / Not Yet Assess
                    st.subheader("🔍 Detail Remarks (Not Comply / Not Yet Assess)")
                    filtered_df = df[df["Accuracy"].isin(["Not Comply", "Not Yet Assess"])]
                    st.dataframe(filtered_df[["SiteID", "SiteName", "Accuracy", "Detail"]], use_container_width=True)
                else:
                    st.error("❗ Kolom 'Accuracy' dan/atau 'Detail' tidak ditemukan dalam sheet.")
            else:
                st.error("❗ Sheet 'DismantlePerangkat' tidak ditemukan dalam file Excel.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")