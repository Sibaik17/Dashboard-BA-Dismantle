import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit_authenticator as stauth

# ===============================
# HARUS DI ATAS: Konfigurasi halaman
# ===============================
st.set_page_config(page_title="Dashboard BA Dismantle", layout="wide")

# ===============================
# OPSIONAL: Generate Hash Baru dari Password
# ===============================
with st.expander("🔐 Generate hashed password (opsional, untuk admin dev use only)"):
    new_password = st.text_input("Masukkan password untuk di-hash", type="password")
    if new_password:
        hashed = stauth.Hasher([new_password]).generate()[0]
        st.code(hashed, language="plaintext")

# ===============================
# KONFIGURASI LOGIN
# ===============================
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": "$2b$12$vBRwDjQmAh3SpZ/Dv48xMOdpeAX90hSIocHg04Y4EIjA1QMbkX2Je"  # hashed admin123
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "ba_dashboard",       # cookie name
    "abcdef123456",       # signature key
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", location="sidebar")

# ===============================
# HANDLE LOGIN
# ===============================
if authentication_status is False:
    st.error("Username atau password salah.")
elif authentication_status is None:
    st.warning("Silakan masukkan username dan password.")
elif authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Selamat datang, {name} 👋")

    # ===============================
    # DASHBOARD UTAMA
    # ===============================
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
                ny_assess_count = (df["Accuracy"] == "NY Assessed").sum()

                # Tampilkan metric ringkasan
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📄 Total Dokumen", total_docs)
                col2.metric("✅ Comply", comply_count)
                col3.metric("❌ Not Comply", not_comply_count)
                col4.metric("⏳ Not Yet Assess", ny_assess_count)

                # Hitung dan tampilkan persentase accuracy
                total_assessed = total_docs - ny_assess_count
                if total_assessed > 0:
                    accuracy_percentage = (comply_count / total_assessed) * 100
                    accuracy_label = f"{accuracy_percentage:.2f}%"
                else:
                    accuracy_label = "N/A"

                st.markdown("### ✅ Persentase Accuracy")
                st.metric(label="Accuracy (%)", value=accuracy_label)
                st.caption("Persentase akurasi ini diukur dengan membandingkan jumlah dokumen comply dibagi dengan total dokumen semuanya dan dikurang dokumen yang belum dilakukan assessment (Not Yet Assess).")

                # === PIE CHART BERDAMPINGAN ===
                center_col = st.columns([1, 2, 1])[1]
                
                # Pie chart distribusi status accuracy
                with center_col:
                    st.subheader("📈 Distribusi Status Accuracy")
                    status_counts = df["Accuracy"].value_counts()
                    fig = px.pie(
                        names=status_counts.index,
                        values=status_counts.values,
                        title="Distribusi Status Accuracy",
                        hole=0.3
                    )
                    fig.update_traces(textinfo='percent+label', hovertemplate="%{label}<br>Value = %{value}<extra></extra>")
                    st.plotly_chart(fig, use_container_width=True)
                
                # PIE CHART REMARKS PER STATUS
                st.subheader("🧾 Distribusi Detail Remarks per Status")

                col_left, col_right = st.columns(2)
                
                # Pie Chart untuk Not Comply
                with col_left:
                    st.markdown("#### ❌ Detail Remarks - Not Comply")
                    not_comply_details = df[df["Accuracy"] == "Not Comply"]["Detail"].value_counts()
                    if not not_comply_details.empty:
                        fig_nc = px.pie(
                            names=not_comply_details.index,
                            values=not_comply_details.values,
                            title="Detail Remarks - Not Comply"
                        )
                        fig_nc.update_traces(textinfo= 'percent+label',
                                             hovertemplate= "%{label}<br>Value = %{value}<br>Percent = %{percent}<extra></extra>"
                                            )
                        st.plotly_chart(fig_nc, use_container_width=True)
                
                # Pie Chart untuk NY Assessed
                with col_right:
                    st.markdown("#### ⏳ Detail Remarks - NY Assessed")
                    ny_assessed_details = df[df["Accuracy"] == "NY Assessed"]["Detail"].value_counts()
                    if not ny_assessed_details.empty:
                        fig_ny = px.pie(
                            names=ny_assessed_details.index,
                            values=ny_assessed_details.values,
                            title="Detail Remarks - Not Yet Assessed"
                        )
                        fig_ny.update_traces(textinfo= 'percent+label',
                                             hovertemplate= "%{label}<br>Value = %{value}<br>Percent = %{percent}<extra></extra>"
                                            )
                        st.plotly_chart(fig_ny, use_container_width=True)

                # Tabel detail Not Comply / Not Yet Assess
                st.subheader("🔍 Detail Remarks (Not Comply / NY Assessed)")
                filtered_df = df[df["Accuracy"].isin(["Not Comply", "NY Assessed"])]
                st.dataframe(filtered_df[["SONumb", "SiteName", "Accuracy", "Detail"]], use_container_width=True)
            else:
                st.error("❗ Sheet 'DismantlePerangkat' tidak ditemukan.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat membaca file: {e}")
