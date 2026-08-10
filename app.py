import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & BRANDING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Professional AI Architect & Engineering", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Identitas Kreator
st.title("🏛️ DELUXY.Ai - AI Architectural & RAB Engineering System")
st.markdown("##### *Created & Developed by **Daffa Hendrawinata***")
st.caption("Platform Asisten Arsitek AI: Desain Visual Realistis, Estimasi Teknik RAB Presisi, dan Konsultasi Solusi Konsumen")
st.markdown("---")

# -------------------------------------------------------------------
# INPUT PARAMETER
# -------------------------------------------------------------------
col_input, col_output = st.columns([1, 2.2])

with col_input:
    st.subheader("⚙️ Parameter Desain & Kebutuhan")
    
    prompt = st.text_area(
        "Deskripsi Impian / Konsep Rumah:", 
        placeholder="Contoh: Rumah minimalis modern budget 500jt, 2 kamar tidur, ada kolam renang kecil di samping dan pencahayaan alami banyak",
        height=100
    )
    
    budget = st.number_input("Target Budget Klien (Rp):", min_value=100000000, value=500000000, step=25000000, format="%d")
    gaya = st.selectbox("Gaya Arsitektur Fasad:", [
        "Minimalis Modern (Clean & Glass)", 
        "Skandinavia / Japandi (Warm Wood & White)", 
        "Mewah Kontemporer (Marble & Luxury Light)", 
        "Industrial Modern (Exposed Brick & Metal)"
    ])
    
    c1, c2 = st.columns(2)
    with c1:
        panjang = st.slider("Panjang Lahan (m):", 8, 30, 15)
        lantai = st.radio("Jumlah Lantai:", [1, 2])
    with c2:
        lebar = st.slider("Lebar Lahan (m):", 6, 20, 10)
        ada_kolam = st.checkbox("Fasilitas Kolam Renang", value=True)
        
    btn_generate = st.button("🚀 Process Architectural Design & Engineering Analysis", use_container_width=True)

# -------------------------------------------------------------------
# FUNGSI KALKULASI ENGINEERING & PERHITUNGAN RIIL
# -------------------------------------------------------------------
def calculate_real_engineering(p, l, jml_lantai, bg_klien, kolam):
    luas_tanah = p * l
    # KDB (Koefisien Dasar Bangunan) rata-rata 60%
    luas_lantai_1 = luas_tanah * 0.6
    luas_bangunan_total = luas_lantai_1 * (1.8 if jml_lantai == 2 else 1.0)
    
    # Standar Biaya Konstruksi Riil Arsitektur (2026)
    biaya_per_m2 = 4800000 if jml_lantai == 1 else 5800000
    est_konstruksi_rumah = luas_bangunan_total * biaya_per_m2
    
    # Estimasi Tambahan Kolam Renang (ukuran 3x6m / opsional)
    biaya_kolam = 75000000 if kolam else 0
    total_est_biaya = est_konstruksi_rumah + biaya_kolam
    
    # Perhitungan Material Teknik Riil
    # 1. Batu Bata (kebutuhan ±70 pcs per m2 dinding, asumsi keliling dinding)
    keliling_dinding = (p + l) * 2 * jml_lantai * 3.5 # tinggi 3.5m
    batu_bata = int(keliling_dinding * 65)
    
    # 2. Semen (sak 50kg)
    semen_sak = int(luas_bangunan_total * 1.35)
    
    # 3. Besi Beton Ulir (10mm & 12mm untuk struktur kolom & sloof)
    besi_batang = int(luas_bangunan_total * 2.8)
    
    # 4. Cat Dinding (Kaleng 25kg)
    cat_kaleng = int((keliling_dinding * 2) / 100) + 1
    
    return luas_tanah, luas_bangunan_total, total_est_biaya, batu_bata, semen_sak, besi_batang, cat_kaleng

# Denah Layout 2D Interaktif
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="#222", width=3), fillcolor="#F9F9F9")
    
    # Ruangan Utama
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.45, y1=l*0.5, fillcolor="#FFE8D6", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.225], y=[l*0.25], text=["<b>Ruang Tamu & Keluarga</b>"], mode="text"))

    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD166", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama + En-suite</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.7, y1=l, fillcolor="#118AB2", opacity=0.3, line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.75], text=["<b>Kamar Anak & KM</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.45, y0=0, x1=p*0.7, y1=l*0.5, fillcolor="#E9ECEF", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.575], y=[l*0.25], text=["<b>Dapur & Area Makan</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.7, y0=0, x1=p, y1=l, fillcolor="#06D6A0", opacity=0.4, line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.85], y=[l*0.5], text=["<b>Taman / Kolam Renang</b>"], mode="text"))

    fig.update_xaxes(title="Lebar Lahan (Meter)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang Lahan (Meter)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# -------------------------------------------------------------------
# AMBIL DAN TAMPILKAN HASIL DESIGN AI
# -------------------------------------------------------------------
with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Analisis Arsitektur & Perhitungan RAB Berhasil Disusun!")
            
            lt, lb, est_biaya, bata, semen, besi, cat = calculate_real_engineering(panjang, lebar, lantai, budget, ada_kolam)
            
            tab_render, tab_rab, tab_solusi, tab_denah = st.tabs([
                "🎨 Visualisasi Design Realistis", 
                "📊 Estimasi RAB & Material Riil", 
                "💡 Konsultasi & Solusi Klien", 
                "📐 Denah Tata Ruang 2D"
            ])
            
            # --- TAB 1: VISUAL RENDER REALISTIS ---
            with tab_render:
                st.subheader("🖼️ Hasil Design Render Eksterior & Interior")
                st.caption("Visualisasi realistis bangunan rumah impian berstandar arsitektur profesional:")
                
                clean_prompt = prompt.replace(" ", "%20")
                gaya_clean = gaya.split(" ")[0].lower()
                
                img_fasad = f"https://image.pollinations.ai/prompt/photorealistic%20architectural%20render%20of%20a%20modern%20{gaya_clean}%20house,%20exterior%20facade,%20{clean_prompt},%20wooden%20door,%20large%20glass%20windows,%20warm%20exterior%20lighting,%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=550&seed=101"
                img_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya_clean}%20style,%20king%20bed,%20ambient%20lighting,%20large%20window%20view?width=512&height=350&seed=22"
                img_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20and%20dining%20area,%20marble%20countertop,%20{gaya_clean}%20style,%20aesthetic%20lighting?width=512&height=350&seed=33"
                
                st.image(img_fasad, caption="Visualisasi Fasad Eksterior & Lanskap Rumah", use_container_width=True)
                
                c_img1, c_img2 = st.columns(2)
                with c_img1:
                    st.image(img_kamar, caption="Konsep Interior Kamar Tidur Utama", use_container_width=True)
                with c_img2:
                    st.image(img_dapur, caption="Konsep Interior Dapur & Kitchen Set", use_container_width=True)

            # --- TAB 2: ESTIMASI BIAYA & MATERIAL RIIL ---
            with tab_rab:
                st.subheader("📊 Perhitungan Rencana Anggaran Biaya (RAB)")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Lahan / Tanah", f"{lt} m²")
                m2.metric("Luas Total Bangunan", f"{lb:.1f} m²")
                m3.metric("Estimasi Total Biaya", f"Rp {est_biaya:,.0f}")
                
                st.markdown("---")
                st.write("#### 🧱 Estimasi Material Utama (Standar Konstruksi Bangunan):")
                
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.write(f"- 🧱 **Bata Merah / Hebel:** ± {bata:,} Pcs")
                    st.write(f"- 📦 **Semen Porland (50kg):** ± {semen:,} Sak")
                with col_m2:
                    st.write(f"- 🏗️ **Besi Beton Ulir (10/12mm):** ± {besi:,} Batang")
                    st.write(f"- 🎨 **Cat Dinding Interior/Eksterior:** ± {cat} Kaleng (25kg)")
                
                st.info("ℹ️ *Catatan Teknik: Perhitungan menggunakan acuan Analisis Harga Satuan Pekerjaan (AHSP) standar konstruksi lantai & struktur.*")

            # --- TAB 3: KONSULTASI & SOLUSI UNTUK KONSUMEN ---
            with tab_solusi:
                st.subheader("💡 Analisis Budget & Rekomendasi Arsitek")
                
                selisih_budget = budget - est_biaya
                
                if selisih_budget < 0:
                    st.error(f"⚠️ **Budget Kurang (Defisit Rp {abs(selisih_budget):,.0f})**")
                    st.markdown("### 🛠️ Solusi & Saran Penghematan dari Arsitek:")
                    st.write("1. **Pembangunan Bertahap (Tumbuh):** Lakukan pembangunan tahap 1 untuk struktur lantai 1 & atap dulu. Lantai 2 / *finishing* kolam renang diselesaikan di tahap berikutnya.")
                    st.write("2. **Optimasi Material (Value Engineering):** Gunakan bata ringan (Hebel) pengganti bata merah untuk menghemat upah tenaga kerja hingga 15%.")
                    st.write("3. **Pengurangan Spesifikasi Kolam:** Mengubah kolam renang permanen menjadi *plunge pool* kecil atau area taman terbuka untuk menghemat budget ± Rp 50.000.000.")
                else:
                    st.success(f"✅ **Budget Aman / Cukup (Sisa Margin: Rp {selisih_budget:,.0f})**")
                    st.markdown("### 🌟 Saran Optimalisasi dari Arsitek:")
                    st.write("1. **Upgrade Material Interior:** Sisa budget dapat dialokasikan untuk penambahan *Smart Home System*, *kitchen set* marmer, atau lantai *granite tile* kualitas tinggi.")
                    st.write("2. **Efisiensi Energi (Green Building):** Gunakan jendela Kaca Low-E dan panel surya atap (*Solar Panel*) untuk menekan biaya listrik jangka panjang.")
                    st.write("3. **Lanskap & Lighting:** Buat pencahayaan taman hias (Lanskap LED) dan sistem drainase kolam renang otomatis.")

            # --- TAB 4: DENAH LAYOUT 2D ---
            with tab_denah:
                st.subheader("📐 Plan Layout Pembagian Ruangan")
                st.caption("Peta denah tata letak proporsional berdasarkan ukuran lahan yang Anda atur:")
                st.plotly_chart(generate_2d_floorplan(panjang, lebar), use_container_width=True)

            # Unduh DXF
            st.markdown("---")
            dxf_data = generate_dxf_file(panjang, lebar)
            st.download_button(
                label="⬇️ Unduh Drafter DXF CAD File",
                data=dxf_data,
                file_name=f"DELUXY_Layout_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan ketikkan deskripsi konsep impian Anda terlebih dahulu.")

# -------------------------------------------------------------------
# FOOTER CREDITS
# -------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #777; font-size: 14px;'>"
    "© 2026 DELUXY.Ai System. Designed & Programmed by <b>Daffa Hendrawinata</b>. All Rights Reserved."
    "</div>", 
    unsafe_allow_html=True
)
