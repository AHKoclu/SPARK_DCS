import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fpdf import FPDF
import tempfile
import os
import json
# Türkçe karakterleri PDF için ascii'ye çevirme
def safe_ascii(text):
st.title("⛽ Spark: IMO DCS Fuel & Voyage Tracker")
st.markdown("*Yeni IMO DCS kurallarına göre **Underway/Not Underway** ve tüketici bazlı yakıt ayırma otomasyonu.*")
# İlk Yükleme (Örnek Verileriniz)
# İlk Yükleme (Örnek Verileriniz veya Kaydedilmiş Veriler)
VOYAGES_FILE = "voyages.csv"
VESSEL_INFO_FILE = "vessel_info.json"
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
    if os.path.exists(VOYAGES_FILE):
        try:
            df = pd.read_csv(VOYAGES_FILE)
            for col in df.columns:
                if col != "Voyage":
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
            st.session_state.voyages = df
        except Exception as e:
            st.error(f"Kayıtlı veri yüklenirken hata oluştu: {e}")
            st.session_state.voyages = pd.DataFrame()
    else:
        df = pd.DataFrame([
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
        for col in df.columns:
            if col != "Voyage":
                df[col] = df[col].astype(float)
        st.session_state.voyages = df
        st.session_state.voyages.to_csv(VOYAGES_FILE, index=False)
if "vessel_info" not in st.session_state:
    if os.path.exists(VESSEL_INFO_FILE):
        try:
            with open(VESSEL_INFO_FILE, "r", encoding="utf-8") as f:
                st.session_state.vessel_info = json.load(f)
        except Exception as e:
            st.session_state.vessel_info = {"vessel_name": "M/V SPARK", "fleet_name": "SPARK Fleet"}
    else:
        st.session_state.vessel_info = {"vessel_name": "M/V SPARK", "fleet_name": "SPARK Fleet"}
        with open(VESSEL_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.vessel_info, f, ensure_ascii=False)
# Sol Menü (Sidebar) - Yeni Voyage Ekleme Alanı (Sarı Alanların Yerine)
with st.sidebar:
    st.header("🚢 Gemi Bilgileri")
    vessel_name = st.text_input("Gemi Adı", "M/V SPARK")
    fleet_name = st.text_input("Filo Adı", "SPARK Fleet")
    vessel_name = st.text_input("Gemi Adı", st.session_state.vessel_info["vessel_name"])
    fleet_name = st.text_input("Filo Adı", st.session_state.vessel_info["fleet_name"])
    
    if (vessel_name != st.session_state.vessel_info["vessel_name"] or 
        fleet_name != st.session_state.vessel_info["fleet_name"]):
        st.session_state.vessel_info = {"vessel_name": vessel_name, "fleet_name": fleet_name}
        with open(VESSEL_INFO_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.vessel_info, f, ensure_ascii=False)
            
    st.divider()
    st.header("➕ Yeni Voyage Ekle (Sarı Alanlar)")
    v_name = st.text_input("Voyage Adı", "Yeni Voyage")
            "U_HFO_ME": u_h_me, "U_HFO_AE": u_h_ae, "U_HFO_BOILER": u_h_bo, "U_HFO_IGG": u_h_ig,
            "U_MGO_ME": u_m_me, "U_MGO_AE": u_m_ae, "U_MGO_BOILER": u_m_bo, "U_MGO_IGG": u_m_ig
        }
        for k in new_row:
            if k != "Voyage":
                new_row[k] = float(new_row[k])
        st.session_state.voyages = pd.concat([st.session_state.voyages, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.voyages.to_csv(VOYAGES_FILE, index=False)
        st.success(f"{v_name} başarıyla eklendi!")
        st.rerun()
st.subheader("📋 Voyage Veritabanı (Düzenlenebilir Tablo)")
st.caption("Eski excel'deki gibi tek tek formül düzeltmenize gerek yok! Herhangi bir voyage hücresini doğrudan bu tabloda değiştirebilirsiniz; üstteki mavi özetler anında güncellenir.")
edited_df = st.data_editor(st.session_state.voyages, num_rows="dynamic", use_container_width=True)
st.session_state.voyages = edited_df
# Ensure types are floats
for col in edited_df.columns:
    if col != "Voyage":
        edited_df[col] = pd.to_numeric(edited_df[col], errors='coerce').fillna(0.0).astype(float)
if not edited_df.equals(st.session_state.voyages):
    st.session_state.voyages = edited_df
    st.session_state.voyages.to_csv(VOYAGES_FILE, index=False)
    st.rerun()
# --- PDF GENERATOR ---
def generate_pdf(v_name, f_name):
    pdf = FPDF()
        mime="application/pdf"
    )
