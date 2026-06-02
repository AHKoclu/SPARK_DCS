import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os

# Türkçe karakterleri PDF için ascii'ye çevirme
def safe_ascii(text):
    mapping = {"ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
               "ö": "o", "Ö": "O", "ş": "s", "Ş": "S", "ü": "u", "Ü": "U"}
    for k, v in mapping.items():
        text = str(text).replace(k, v)
    return text

st.set_page_config(page_title="IMO DCS Fuel Tracker", layout="wide", page_icon="⛽")

st.title("⛽ MarineDeCarb: IMO DCS Fuel & Voyage Tracker")
st.markdown("*Yeni IMO DCS kurallarına göre **Underway/Not Underway** ve tüketici bazlı yakıt ayırma otomasyonu.*")

# İlk Yükleme (Örnek Verileriniz)
if "voyages" not in st.session_state:
    st.session_state.voyages = pd.DataFrame([
        {"Voyage": "Voyage 05/2025", 
         "NU_HFO_ME": 0.0, "NU_HFO_AE": 22.35, "NU_HFO_BOILER": 0.0, "NU_HFO_IGG": 0.0,
         "NU_MGO_ME": 1.25, "NU_MGO_AE": 9.56, "NU_MGO_BOILER": 0.0, "NU_MGO_IGG": 0.0,
         "U_HFO_ME": 191.07, "U_HFO_AE": 22.05, "U_HFO_BOILER": 0.0, "U_HFO_IGG": 0.0,
         "U_MGO_ME": 1.0, "U_MGO_AE": 1.06, "U_MGO_BOILER": 0.1, "U_MGO_IGG": 6.0},
        {"Voyage": "Voyage -01-26", 
         "NU_HFO_ME": 58.97, "NU_HFO_AE": 67.6, "NU_HFO_BOILER": 0.0, "NU_HFO_IGG": 0.0,
         "NU_MGO_ME": 14.17, "NU_MGO_AE": 145.91, "NU_MGO_BOILER": 22.8, "NU_MGO_IGG": 0.0,
         "U_HFO_ME": 589.49, "U_HFO_AE": 64.4, "U_HFO_BOILER": 0.0, "U_HFO_IGG": 0.0,
         "U_MGO_ME": 31.35, "U_MGO_AE": 6.15, "U_MGO_BOILER": 0.0, "U_MGO_IGG": 0.0},
        {"Voyage": "Voyage -02-26", 
         "NU_HFO_ME": 0.76, "NU_HFO_AE": 24.83, "NU_HFO_BOILER": 9.2, "NU_HFO_IGG": 0.0,
         "NU_MGO_ME": 40.26, "NU_MGO_AE": 20.76, "NU_MGO_BOILER": 4.09, "NU_MGO_IGG": 0.0,
         "U_HFO_ME": 345.03, "U_HFO_AE": 37.51, "U_HFO_BOILER": 0.0, "U_HFO_IGG": 0.0,
         "U_MGO_ME": 414.78, "U_MGO_AE": 62.15, "U_MGO_BOILER": 2.5, "U_MGO_IGG": 0.0}
    ])

# Sol Menü (Sidebar) - Yeni Voyage Ekleme Alanı (Sarı Alanların Yerine)
with st.sidebar:
    st.header("🚢 Gemi Bilgileri")
    vessel_name = st.text_input("Gemi Adı", "M/V Marine")
    fleet_name = st.text_input("Filo Adı", "MarineDeCarb Fleet")
    st.divider()
    st.header("➕ Yeni Voyage Ekle (Sarı Alanlar)")
    v_name = st.text_input("Voyage Adı", "Yeni Voyage")
    
    st.subheader("🛑 NOT UNDERWAY (HFO)")
    c1, c2 = st.columns(2)
    nu_h_me = c1.number_input("ME (HFO) NU", 0.0, step=1.0)
    nu_h_ae = c2.number_input("AE (HFO) NU", 0.0, step=1.0)
    nu_h_bo = c1.number_input("BOILER (HFO) NU", 0.0, step=1.0)
    nu_h_ig = c2.number_input("OTHERS (HFO) NU", 0.0, step=1.0)
    
    st.subheader("🛑 NOT UNDERWAY (MGO)")
    c3, c4 = st.columns(2)
    nu_m_me = c3.number_input("ME (MGO) NU", 0.0, step=1.0)
    nu_m_ae = c4.number_input("AE (MGO) NU", 0.0, step=1.0)
    nu_m_bo = c3.number_input("BOILER (MGO) NU", 0.0, step=1.0)
    nu_m_ig = c4.number_input("OTHERS (MGO) NU", 0.0, step=1.0)

    st.subheader("🌊 UNDERWAY (HFO)")
    c5, c6 = st.columns(2)
    u_h_me = c5.number_input("ME (HFO) U", 0.0, step=1.0)
    u_h_ae = c6.number_input("AE (HFO) U", 0.0, step=1.0)
    u_h_bo = c5.number_input("BOILER (HFO) U", 0.0, step=1.0)
    u_h_ig = c6.number_input("OTHERS (HFO) U", 0.0, step=1.0)
    
    st.subheader("🌊 UNDERWAY (MGO)")
    c7, c8 = st.columns(2)
    u_m_me = c7.number_input("ME (MGO) U", 0.0, step=1.0)
    u_m_ae = c8.number_input("AE (MGO) U", 0.0, step=1.0)
    u_m_bo = c7.number_input("BOILER (MGO) U", 0.0, step=1.0)
    u_m_ig = c8.number_input("OTHERS (MGO) U", 0.0, step=1.0)

    if st.button("➕ Voyage'ı Veritabanına Ekle", type="primary"):
        new_row = {
            "Voyage": v_name,
            "NU_HFO_ME": nu_h_me, "NU_HFO_AE": nu_h_ae, "NU_HFO_BOILER": nu_h_bo, "NU_HFO_IGG": nu_h_ig,
            "NU_MGO_ME": nu_m_me, "NU_MGO_AE": nu_m_ae, "NU_MGO_BOILER": nu_m_bo, "NU_MGO_IGG": nu_m_ig,
            "U_HFO_ME": u_h_me, "U_HFO_AE": u_h_ae, "U_HFO_BOILER": u_h_bo, "U_HFO_IGG": u_h_ig,
            "U_MGO_ME": u_m_me, "U_MGO_AE": u_m_ae, "U_MGO_BOILER": u_m_bo, "U_MGO_IGG": u_m_ig
        }
        st.session_state.voyages = pd.concat([st.session_state.voyages, pd.DataFrame([new_row])], ignore_index=True)
        st.success(f"{v_name} başarıyla eklendi!")
        st.rerun()

# --- MAVİ ALANLAR (OTOMATİK HESAPLAMALAR) ---
df = st.session_state.voyages

# HFO Totals
tot_hfo_me = df["NU_HFO_ME"].sum() + df["U_HFO_ME"].sum()
tot_hfo_ae = df["NU_HFO_AE"].sum() + df["U_HFO_AE"].sum()
tot_hfo_bo = df["NU_HFO_BOILER"].sum() + df["U_HFO_BOILER"].sum()
tot_hfo_ig = df["NU_HFO_IGG"].sum() + df["U_HFO_IGG"].sum()
grand_hfo = tot_hfo_me + tot_hfo_ae + tot_hfo_bo + tot_hfo_ig

# MGO Totals
tot_mgo_me = df["NU_MGO_ME"].sum() + df["U_MGO_ME"].sum()
tot_mgo_ae = df["NU_MGO_AE"].sum() + df["U_MGO_AE"].sum()
tot_mgo_bo = df["NU_MGO_BOILER"].sum() + df["U_MGO_BOILER"].sum()
tot_mgo_ig = df["NU_MGO_IGG"].sum() + df["U_MGO_IGG"].sum()
grand_mgo = tot_mgo_me + tot_mgo_ae + tot_mgo_bo + tot_mgo_ig

# Not Underway Totals
nu_hfo_me = df["NU_HFO_ME"].sum()
nu_hfo_ae = df["NU_HFO_AE"].sum()
nu_hfo_bo = df["NU_HFO_BOILER"].sum()
nu_hfo_ig = df["NU_HFO_IGG"].sum()

nu_mgo_me = df["NU_MGO_ME"].sum()
nu_mgo_ae = df["NU_MGO_AE"].sum()
nu_mgo_bo = df["NU_MGO_BOILER"].sum()
nu_mgo_ig = df["NU_MGO_IGG"].sum()

# Underway Totals
u_hfo_me = df["U_HFO_ME"].sum()
u_hfo_ae = df["U_HFO_AE"].sum()
u_hfo_bo = df["U_HFO_BOILER"].sum()
u_hfo_ig = df["U_HFO_IGG"].sum()

u_mgo_me = df["U_MGO_ME"].sum()
u_mgo_ae = df["U_MGO_AE"].sum()
u_mgo_bo = df["U_MGO_BOILER"].sum()
u_mgo_ig = df["U_MGO_IGG"].sum()

# Top KPIs
c1, c2 = st.columns(2)
c1.metric("🌍 GRAND TOTAL HFO", f"{grand_hfo:,.2f} MT")
c2.metric("🌍 GRAND TOTAL MGO", f"{grand_mgo:,.2f} MT")
st.divider()

# Summaries (Mavi Formüllü Alanların Karşılığı)
st.subheader("📊 Otomatik Tüketim Özetleri (Excel'deki Mavi Alanlar)")

col1, col2 = st.columns(2)
with col1:
    st.info("🔥 TOTAL HFO BREAKDOWN")
    st.write(f"**TOTAL ME:** {tot_hfo_me:,.2f}")
    st.write(f"**TOTAL AE:** {tot_hfo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {tot_hfo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS (IGG vb):** {tot_hfo_ig:,.2f}")
    
    st.warning("🛑 NOT UNDERWAY TOTAL HFO")
    st.write(f"**TOTAL ME:** {nu_hfo_me:,.2f}")
    st.write(f"**TOTAL AE:** {nu_hfo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {nu_hfo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS:** {nu_hfo_ig:,.2f}")

    st.success("🌊 UNDERWAY TOTAL HFO")
    st.write(f"**TOTAL ME:** {u_hfo_me:,.2f}")
    st.write(f"**TOTAL AE:** {u_hfo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {u_hfo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS:** {u_hfo_ig:,.2f}")

with col2:
    st.info("⚡ TOTAL MGO BREAKDOWN")
    st.write(f"**TOTAL ME:** {tot_mgo_me:,.2f}")
    st.write(f"**TOTAL AE:** {tot_mgo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {tot_mgo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS (IGG vb):** {tot_mgo_ig:,.2f}")
    
    st.warning("🛑 NOT UNDERWAY TOTAL MGO")
    st.write(f"**TOTAL ME:** {nu_mgo_me:,.2f}")
    st.write(f"**TOTAL AE:** {nu_mgo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {nu_mgo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS:** {nu_mgo_ig:,.2f}")

    st.success("🌊 UNDERWAY TOTAL MGO")
    st.write(f"**TOTAL ME:** {u_mgo_me:,.2f}")
    st.write(f"**TOTAL AE:** {u_mgo_ae:,.2f}")
    st.write(f"**TOTAL BOILER:** {u_mgo_bo:,.2f}")
    st.write(f"**TOTAL OTHERS:** {u_mgo_ig:,.2f}")

st.divider()

st.subheader("📋 Voyage Veritabanı (Düzenlenebilir Tablo)")
st.caption("Eski excel'deki gibi tek tek formül düzeltmenize gerek yok! Herhangi bir voyage hücresini doğrudan bu tabloda değiştirebilirsiniz; üstteki mavi özetler anında güncellenir.")
edited_df = st.data_editor(st.session_state.voyages, num_rows="dynamic", use_container_width=True)
st.session_state.voyages = edited_df

# --- PDF GENERATOR ---
def generate_pdf(v_name, f_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(190, 10, safe_ascii("MarineDeCarb IMO DCS Fuel Tracker Report"), ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, safe_ascii(f"Gemi Adı: {v_name}"), ln=True)
    pdf.cell(190, 10, safe_ascii(f"Filo Adı: {f_name}"), ln=True)
    pdf.line(10, 45, 200, 45)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "1. GRAND TOTALS", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(95, 8, f"TOTAL HFO: {grand_hfo:,.2f} MT")
    pdf.cell(95, 8, f"TOTAL MGO: {grand_mgo:,.2f} MT", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(95, 10, "2. HFO BREAKDOWN", 0, 0)
    pdf.cell(95, 10, "3. MGO BREAKDOWN", 0, 1)
    pdf.set_font("Helvetica", "", 10)
    
    pdf.cell(95, 8, f"ME: {tot_hfo_me:,.2f} | AE: {tot_hfo_ae:,.2f}", 0, 0)
    pdf.cell(95, 8, f"ME: {tot_mgo_me:,.2f} | AE: {tot_mgo_ae:,.2f}", 0, 1)
    pdf.cell(95, 8, f"BOILER: {tot_hfo_bo:,.2f} | OTHERS: {tot_hfo_ig:,.2f}", 0, 0)
    pdf.cell(95, 8, f"BOILER: {tot_mgo_bo:,.2f} | OTHERS: {tot_mgo_ig:,.2f}", 0, 1)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "4. NOT UNDERWAY (NU) SUMMARY", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 8, f"NU HFO -> ME:{nu_hfo_me:.2f} | AE:{nu_hfo_ae:.2f} | BO:{nu_hfo_bo:.2f} | IG:{nu_hfo_ig:.2f}")
    pdf.cell(95, 8, f"NU MGO -> ME:{nu_mgo_me:.2f} | AE:{nu_mgo_ae:.2f} | BO:{nu_mgo_bo:.2f} | IG:{nu_mgo_ig:.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(190, 10, "5. UNDERWAY (U) SUMMARY", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(95, 8, f"U HFO -> ME:{u_hfo_me:.2f} | AE:{u_hfo_ae:.2f} | BO:{u_hfo_bo:.2f} | IG:{u_hfo_ig:.2f}")
    pdf.cell(95, 8, f"U MGO -> ME:{u_mgo_me:.2f} | AE:{u_mgo_ae:.2f} | BO:{u_mgo_bo:.2f} | IG:{u_mgo_ig:.2f}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(190, 5, safe_ascii("* Generated automatically by MarineDeCarb Simulator."), ln=True)
    
    tmp_path = os.path.join(tempfile.gettempdir(), "IMO_DCS_Fuel_Report.pdf")
    pdf.output(tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    return data

st.sidebar.divider()
st.sidebar.header("📥 Raporlama")
if st.sidebar.button("📄 PDF Rapor İndir"):
    pdf_bytes = generate_pdf(vessel_name, fleet_name)
    st.sidebar.download_button(
        label="💾 Raporu Kaydet", 
        data=pdf_bytes, 
        file_name="IMO_DCS_Fuel_Report.pdf", 
        mime="application/pdf"
    )
