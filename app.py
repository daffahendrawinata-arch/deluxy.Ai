import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & BRANDING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Professional Human-Touch Architectural Engine", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Identitas Kreator
st.title("🏛️ DELUXY.Ai - AI Architectural & RAB Engineering System")
st.markdown("##### *Created & Developed by **Daffa Hendrawinata***")
st.caption("Platform Modeler 3D Interaktif, Simulasi Material Presisi, dan Engine Solusi Konsultasi Klien")
st.markdown("---")

# -------------------------------------------------------------------
# INPUT PARAMETER
# -------------------------------------------------------------------
col_input, col_output = st.columns([1, 2.2])

with col_input:
    st.subheader("⚙️ Parameter & Kebutuhan Klien")
    
    prompt = st.text_area(
        "Deskripsi Konsep Impian Klien:", 
        placeholder="Contoh: Rumah minimalis modern budget 500jt, 2 kamar tidur, ada kolam renang dan fasad kayu modern",
        height=100
    )
    
    budget = st.number_input("Target Budget Klien (Rp):", min_value=100000000, value=500000000, step=25000000, format="%d")
    gaya = st.selectbox("Gaya Arsitektur:", [
        "Minimalis Modern (Clean Glass & Wood)", 
        "Skandinavia / Japandi (Warm Earthy)", 
        "Mewah Kontemporer (Luxury Lighting)", 
        "Industrial Modern (Exposed Brick & Iron)"
    ])
    
    c1, c2 = st.columns(2)
    with c1:
        panjang = st.slider("Panjang Lahan (m):", 8, 30, 15)
        lantai = st.radio("Jumlah Lantai:", [1, 2])
    with c2:
        lebar = st.slider("Lebar Lahan (m):", 6, 20, 10)
        ada_kolam = st.checkbox("Fasilitas Kolam Renang", value=True)
        
    btn_generate = st.button("🚀 Render Model 3D & Kalkulasi Engineering", use_container_width=True)

# -------------------------------------------------------------------
# HELPER MESH 3D ARSITEKTUR REALISTIS
# -------------------------------------------------------------------
def add_box_3d(fig, x0, x1, y0, y1, z0, z1, color, opacity=1.0, name=""):
    x = [x0, x1, x1, x0, x0, x1, x1, x0]
    y = [y0, y0, y1, y1, y0, y0, y1, y1]
    z = [z0, z0, z0, z0, z1, z1, z1, z1]
    i = [7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]
    j = [3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6]
    k = [0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2]
    fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opacity, name=name, showlegend=False))

# -------------------------------------------------------------------
# ENGINE MODEL 3D DENGAN DETAIL HUMAN-TOUCH (SketchUp Style)
# -------------------------------------------------------------------
def generate_human_like_3d_model(p, l, jml_lantai, kolam):
    fig = go.Figure()
    h_lantai = 3.5 * jml_lantai

    # 1. Rumput Lanskap & Ground
    add_box_3d(fig, -2, p+2, -2, l+2, -0.15, 0.0, '#3A5A40', name="Halaman Rumput")
    
    # 2. Walkway / Carport (Beton Grey)
    add_box_3d(fig, 0, p*0.3, -1.8, 0, 0.0, 0.05, '#A3B18A', name="Carport")

    # 3. Lantai / Pedestal Utama Bangunan
    add_box_3d(fig, 0, p*0.65, 0, l*0.85, 0.0, 0.2, '#E9ECEF', name="Lantai Teras")

    # 4. Dinding Utama (Off-White Warm Architecture)
    add_box_3d(fig, 0, p*0.65, 0, l*0.85, 0.2, h_lantai, '#F8F9FA', opacity=0.98, name="Dinding Utama")

    # 5. Detail Fasad Kayu Accent (Muka Depan)
    add_box_3d(fig, p*0.2, p*0.65, -0.05, 0.0, 0.2, h_lantai, '#6F4E37', name="Panel Kayu Fasad")

    # 6. PINTU UTAMA PRESISI (Kusen + Daun Pintu Kayu + Gagang Metal)
    # Kusen Pintu
    add_box_3d(fig, p*0.08, p*0.19, -0.06, 0.02, 0.2, h_lantai*0.68, '#2B1B17', name="Kusen Pintu")
    # Daun Pintu
    add_box_3d(fig, p*0.09, p*0.18, -0.07, -0.02, 0.2, h_lantai*0.66, '#8B4513', name="Pintu Utama Kayu")
    # Gagang Pintu Stainless
    add_box_3d(fig, p*0.16, p*0.17, -0.10, -0.07, h_lantai*0.3, h_lantai*0.35, '#D4AF37', name="Gagang Pintu Gold")

    # 7. JENDELA FASAD UTAMA (Frame Aluminium Hitam + Glass Multi-Pane)
    # Jendela Utama Depan (Frame)
    add_box_3d(fig, p*0.25, p*0.58, -0.06, 0.02, h_lantai*0.3, h_lantai*0.85, '#1A1A1A', name="Kusen Jendela")
    # Kaca Transparan Blue Tint
    add_box_3d(fig, p*0.26, p*0.57, -0.07, -0.01, h_lantai*0.32, h_lantai*0.83, '#4EA8DE', opacity=0.6, name="Kaca Jendela Depan")
    # Pembatas Frame Tengah Jendela (List MULLION)
    add_box_3d(fig, p*0.41, p*0.42, -0.08, -0.01, h_lantai*0.32, h_lantai*0.83, '#1A1A1A', name="Frame Mullion")

    # 8. JENDELA LANTAI 2 (Jika 2 Lantai)
    if jml_lantai == 2:
        add_box_3d(fig, p*0.1, p*0.5, -0.06, 0.02, h_lantai*0.58, h_lantai*0.88, '#1A1A1A', name="Kusen Jendela L2")
        add_box_3d(fig, p*0.11, p*0.49, -0.07, -0.01, h_lantai*0.6, h_lantai*0.86, '#4EA8DE', opacity=0.6, name="Kaca L2")
        # Balkon Railing Kaca
        add_box_3d(fig, 0, p*0.65, -0.4, -0.05, h_lantai*0.5, h_lantai*0.55, '#212529', name="Balkon Frame")

    # 9. ATAP MODERN & CANOPY (Slab Flat + Ridge Canopy)
    # Canopy Teras Minimalis
    add_box_3d(fig, -0.2, p*0.67, -0.5, 0.5, h_lantai*0.5 if jml_lantai==1 else h_lantai*0.48, (h_lantai*0.5 if jml_lantai==1 else h_lantai*0.48)+0.15, '#212529', name="Canopy Fasad")
    # Atap Utama Limas
    x_roof = [0, p*0.65, p*0.65, 0, (p*0.65)/2]
    y_roof = [0, 0, l*0.85, l*0.85, (l*0.85)/2]
    z_roof = [h_lantai, h_lantai, h_lantai, h_lantai, h_lantai + 2.0]
    fig.add_trace(go.Mesh3d(x=x_roof, y=y_roof, z=z_roof, i=[0,1,2,3], j=[1,2,3,0], k=[4,4,4,4], color='#4A4E69', opacity=1.0, name="Atap Utama"))

    # 10. KOLAM RENANG ARSITEKTUR & VEGETASI POHON 3D
    if kolam:
        # Dek Kayu Kolam (Pool Deck)
        add_box_3d(fig, p*0.68, p*0.98, 0, l*0.85, 0.0, 0.1, '#D4A373', name="Pool Deck")
        # Dinding Dalam Kolam (Keramik Biru)
        add_box_3d(fig, p*0.72, p*0.94, l*0.15, l*0.7, -0.8, 0.0, '#0077B6', name="Keramik Kolam")
        # Air Kolam (Transparan Cyan)
        add_box_3d(fig, p*0.725, p*0.935, l*0.16, l*0.69, -0.7, -0.05, '#90E0EF', opacity=0.7, name="Air Kolam")

    # Pohon Hias 3D Lanskap (Batang + Daun)
    add_box_3d(fig, -1.2, -0.9, l*0.7, l*0.8, 0.0, 2.2, '#5C4033', name="Batang Pohon")
    add_box_3d(fig, -1.6, -0.5, l*0.6, l*0.9, 2.2, 4.0, '#2D6A4F', opacity=0.9, name="Daun Pohon")

    # Scaling Camera Setup
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)', backgroundcolor="#F8F9FA"),
            yaxis=dict(title='Lebar (m)', backgroundcolor="#F8F9FA"),
            zaxis=dict(title='Tinggi (m)', backgroundcolor="#F8F9FA"),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.6, y=-1.6, z=1.2))
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=520
    )
    return fig

# -------------------------------------------------------------------
# ENGINE KALKULASI ENGINEERING & PERHITUNGAN BIYA REALISTIS
# -------------------------------------------------------------------
def calculate_real_engineering(p, l, jml_lantai, bg_klien, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.6
    luas_bangunan_total = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    biaya_per_m2 = 4750000 if jml_lantai == 1 else 5750000
    est_konstruksi_rumah = luas_bangunan_total * biaya_per_m2
    
    biaya_kolam = 65000000 if kolam else 0
    total_est_biaya = est_konstruksi_rumah + biaya_kolam
    
    # Material SNI / AHSP Standard
    keliling_dinding = (p + l) * 2 * jml_lantai * 3.5
    batu_bata = int(keliling_dinding * 68)
    semen_sak = int(luas_bangunan_total * 1.3)
    besi_batang = int(luas_bangunan_total * 2.7)
    cat_kaleng = int((keliling_dinding * 2) / 95) + 1
    
    return luas_tanah, luas_bangunan_total, total_est_biaya, batu_bata, semen_sak, besi_batang, cat_kaleng

# Denah Layout 2D
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="#222", width=3), fillcolor="#F9F9F9")
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.45, y1=l*0.5, fillcolor="#FFE8D6", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.225], y=[l*0.25], text=["<b>Ruang Tamu & Utm</b>"], mode="text"))
    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD166", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.65, y1=l, fillcolor="#118AB2", opacity=0.3, line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.525], y=[l*0.75], text=["<b>Kamar Anak</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.45, y0=0, x1=p*0.65, y1=l*0.5, fillcolor="#E9ECEF", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.25], text=["<b>Dapur & Makan</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.65, y0=0, x1=p, y1=l, fillcolor="#06D6A0", opacity=0.4, line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.825], y=[l*0.5], text=["<b>Kolam & Deck</b>"], mode="text"))
    fig.update_xaxes(title="Lebar Lahan (Meter)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang Lahan (Meter)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# -------------------------------------------------------------------
# DISPLAY OUTPUT
# -------------------------------------------------------------------
with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Model 3D Interaktif & Perhitungan RAB Teknik Berhasil Dibuat!")
            
            lt, lb, est_biaya, bata, semen, besi, cat = calculate_real_engineering(panjang, lebar, lantai, budget, ada_kolam)
            
            tab_3d, tab_render, tab_rab, tab_solusi = st.tabs([
                "🏠 Model 3D CAD Interaktif", 
                "📸 Visual Render Realistis", 
                "📊 RAB & Material SNI", 
                "💡 Konsultasi & Solusi Klien"
            ])
            
            # --- TAB 1: MODEL 3D CAD INTERAKSI (HUMAN-TOUCH STYLE) ---
            with tab_3d:
                st.subheader("🏠 Model 3D CAD Fasad Interaktif")
                st.caption("Gunakan mouse untuk memutar (orbit), zoom, dan melihat detail kusen pintu kayu, jendela kaca, canopy, serta kolam renang:")
                st.plotly_chart(generate_human_like_3d_model(panjang, lebar, lantai, ada_kolam), use_container_width=True)

            # --- TAB 2: VISUAL FOTO RENDERING REALISTIS ---
            with tab_render:
                st.subheader("🖼️ Hasil Render Visual Realistis Arsitektur")
                st.caption("Prediksi wujud fisik bangunan nyata berdasarkan gaya arsitektur yang dipilih:")
                clean_prompt = prompt.replace(" ", "%20")
                gaya_clean = gaya.split(" ")[0].lower()
                
                img_fasad = f"https://image.pollinations.ai/prompt/photorealistic%20architectural%20render%20of%20a%20modern%20{gaya_clean}%20house,%20exterior%20facade,%20{clean_prompt},%20wooden%20door,%20large%20glass%20windows,%20warm%20lighting,%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=550&seed=101"
                st.image(img_fasad, caption="Fasad Eksterior Hasil Olah Visual", use_container_width=True)

            # --- TAB 3: PERHITUNGAN RAB MATERIAL ---
            with tab_rab:
                st.subheader("📊 Estimasi Anggaran (RAB) & Kebutuhan Material SNI")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Tanah", f"{lt} m²")
                m2.metric("Luas Bangunan Total", f"{lb:.1f} m²")
                m3.metric("Estimasi Total Biaya", f"Rp {est_biaya:,.0f}")
                
                st.markdown("---")
                st.write("#### 🧱 Rincian Material Utama (Berdasarkan Luasan Structur):")
                
                c_mat1, c_mat2 = st.columns(2)
                with c_mat1:
                    st.write(f"- 🧱 **Bata Merah / Hebel:** ± {bata:,} Pcs")
                    st.write(f"- 📦 **Semen Portland (50kg):** ± {semen:,} Sak")
                with c_mat2:
                    st.write(f"- 🏗️ **Besi Beton Structur:** ± {besi:,} Batang")
                    st.write(f"- 🎨 **Cat Dinding (25kg):** ± {cat} Kaleng")

            # --- TAB 4: SOLUSI KONSULTASI BIAYA & ARSITEK ---
            with tab_solusi:
                st.subheader("💡 Analisis Biaya & Solusi Arsitek untuk Klien")
                
                selisih_budget = budget - est_biaya
                
                if selisih_budget < 0:
                    st.error(f"⚠️ **Estimasi Biaya Melebihi Target Budget Klien (Defisit: Rp {abs(selisih_budget):,.0f})**")
                    st.markdown("### 🛠️ Rekomendasi Solusi Penghematan dari Arsitek:")
                    st.write("1. **Skema Rumah Tumbuh:** Utamakan penyelesaian struktur utama lantai 1 terlebih dahulu. Pekerjaan *finishing* lantai 2 atau kolam dapat dialokasikan ke tahap selanjutnya.")
                    st.write("2. **Pengalihan Material Dinding:** Menggunakan Dinding Bata Ringan (Hebel) yang memangkas biaya durasi pengerjaan tukang hingga 15-20%.")
                    st.write("3. **Penyesuaian Area Outdoor:** Mengubah kolam renang permanen menjadi taman kering (*dry garden*) modern untuk menghemat biaya modal awal sebesar ± Rp 65.000.000.")
                else:
                    st.success(f"✅ **Budget Klien Sangat Cukup (Sisa Budget: Rp {selisih_budget:,.0f})**")
                    st.markdown("### 🌟 Rekomendasi Optimalisasi Kualitas:")
                    st.write("1. **Peningkatan Spesifikasi Material:** Mengalokasikan sisa budget pada material penutup lantai (*Granite Tile 80x80cm*) dan sanitary ware berkualitas tinggi.")
                    st.write("2. **Fitur Smart Home & Solar Panel:** Mengintegrasikan kunci pintu otomatis (*Smart Lock*), sakelar pintar, serta panel surya untuk efisiensi energi.")
                    st.write("3. **Lighting & Landscape:** Menambahkan pencahayaan fasad LED (*Warm White Architectural Light*) untuk memberikan kesan mewah pada malam hari.")

            st.markdown("---")
            st.download_button(
                label="⬇️ Unduh File Drafter CAD (.dxf)",
                data=generate_dxf_file(panjang, lebar),
                file_name=f"DELUXY_Layout_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan isi deskripsi konsep terlebih dahulu.")

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
