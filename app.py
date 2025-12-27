pip install geopandas
import streamlit as st
import geopandas as gpd
from streamlit_folium import st_folium
import os

# Import fungsi buatan kita sendiri dari file sebelah
from peta_utils import generate_flood_map

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Flood Susceptibility Map",
    page_icon="🌊",
    layout="wide"
)

# --- JUDUL & DESKRIPSI ---
st.title("🌊 Peta Kerentanan Banjir Jabodetabek")
st.markdown("""
Aplikasi ini menampilkan hasil analisis spasial prediksi banjir menggunakan algoritma 
**Machine Learning (Random Forest)**. Model dilatih berdasarkan parameter fisik wilayah:
- **Slope (Kemiringan Lereng)**
- **Elevation (Ketinggian Lahan)**
- **Land Cover (Tutupan Lahan)**
""")

# --- SIDEBAR (PANEL SAMPING) ---
with st.sidebar:
    st.header("Informasi Proyek")
    st.info("""
    **Metode:** Random Forest Classifier  
    **Akurasi Model:** 87.62%  
    **Area:** Jabodetabek  
    **Data:** Kaggle & Google Earth Engine
    """)
    st.write("---")
    st.write("Dibuat oleh: Yoga Albi Mustofa")
    st.write("Dibuat oleh: Lalu Muhammad Zaqi Arifiandi")
    st.write("Dibuat oleh: Imam Faqih Arrijal")

# --- LOAD DATA (DENGAN CACHE AGAR CEPAT) ---
@st.cache_data
def load_shapefile():
    # Pastikan file .shp, .shx, .dbf ada di satu folder
    return gpd.read_file('Jabodetabek.shp')

# --- LOGIKA UTAMA ---
col1, col2 = st.columns([3, 1])

with col1:
    try:
        # 1. Load Data
        with st.spinner("Memuat data geospasial..."):
            batas_gdf = load_shapefile()
            raster_file = 'Flood_susceptibility.tif'
            
            # Cek apakah file raster ada
            if not os.path.exists(raster_file):
                st.error(f"File {raster_file} tidak ditemukan! Pastikan sudah diupload.")
            else:
                # 2. Panggil fungsi pemetaan dari peta_utils.py
                map_obj = generate_flood_map(batas_gdf, raster_file)
                
                # 3. Tampilkan Peta
                st_folium(map_obj, width="100%", height=600)

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")

with col2:
    st.subheader("Keterangan Legenda")
    # Membuat legenda manual sederhana dengan Markdown/HTML
    st.markdown("""
    <div style="background: linear-gradient(to right, blue, red); height: 20px; width: 100%; border-radius: 5px;"></div>
    <div style="display: flex; justify-content: space-between;">
        <span><b>Rendah (Aman)</b></span>
        <span><b>Tinggi (Rawan)</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    st.write("""
    **Warna Merah:** Menunjukkan area dengan probabilitas banjir yang tinggi. Biasanya berada di dataran rendah atau area dengan drainase buruk.
    
    **Warna Biru:** Menunjukkan area dengan probabilitas banjir rendah (aman). Biasanya dataran tinggi.

    """)
