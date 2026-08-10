import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & BRANDING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Architectural & Engineering System", 
    page_icon="🏛️", 
    layout="wide"
)

# Header Utama (Satu-satunya Penempatan Nama)
st.title("🏛️ DELUXY.Ai - Architectural & Civil Engineering Platform")
st.markdown("##### *Lead Engineer & Developer: **Daffa Hendrawinata***")
st.caption("Sistem Pemodelan BIM, Rendering Visual Realistis, Estimasi RAB SNI, dan Konsultasi Klien")
st.markdown("---")

# -------------------------------------------------------------------
# INPUT PARAMETER
# -------------------------------------------------------------------
col_input, col_output = st.columns([1, 2.2])

with col_input:
    st.subheader("⚙️ Parameter Teknis & Spesifikasi")
    
    prompt = st.text_area(
        "Deskripsi Kebutuhan Klien:", 
        placeholder="Contoh: Rumah 2 lantai minimalis modern budget 600jt, 3 kamar tidur, pencahayaan alami, ada kolam renang",
        height=100
    )
    
    budget = st.number_input("Target Anggaran / Budget Klien (Rp):", min_value=100000000, value=600000000, step=25000000, format="%d")
    gaya = st.selectbox("Gaya Fasad Arsitektur:", [
        "Minimalis Modern (Clean Glass & Concrete)", 
        "Skandinavia / Japandi (Warm Wood & Light)", 
        "Mewah Kontemporer (Luxury Marble)", 
        "Industrial Modern (Exposed Metal & Brick)"
    ])
    
    c1, c2 = st.columns(2)
    with c1:
        panjang = st.slider("Panjang Lahan (m):", 8, 30, 15)
        lantai = st.radio("Jumlah Lantai:", [1, 2])
    with c2:
        lebar = st.slider("Lebar Lahan (m):", 6, 20, 10)
        ada_kolam = st.checkbox("Fasilitas Kolam Renang", value=True)
        
    btn_generate = st.button("🚀 Process Architectural & Engineering Model", use_container_width=True)

# -------------------------------------------------------------------
# 3D BIM WIREFRAME & STRUCTURE MODEL (STANDAR REVIT / AUTOCAD)
# -------------------------------------------------------------------
def generate_engineering_3d_bim(p, l, jml_lantai, kolam):
    fig = go.Figure()
    h_lantai = 3.5 * jml_lantai

    # Outlines / Grid Lahan (Garis Putus-Putus Teknis)
    fig.add_trace(go.Scatter3d(
        x=[0, p, p, 0, 0],
        y=[0, 0, l, l, 0],
        z=[0, 0, 0, 0, 0],
        mode='lines', line=dict(color='#888888', width=3, dash='dash'),
        name="Batas Lahan"
    ))

    # Struktur Kolom Utama (Besi/Beton)
    x_kolom = [0, p*0.6, p*0.6, 0, 0, p*0.6, p*0.6, 0]
    y_kolom = [0, 0, l*0.8, l*0.8, 0, 0, l*0.8, l*0.8]
    z_bottom = [0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai]
    
    for x, y in zip(x_kolom[:4], y_kolom[:4]):
        fig.add_trace(go.Scatter3d(
            x=[x, x], y=[y, y], z=[0, h_lantai],
            mode='lines', line=dict(color='#2B2D42', width=6),
            showlegend=False
        ))

    # Rangka Ring Balk & Sloof (Garis Struktur)
    # Floor 1 Sloof
    fig.add_trace(go.Scatter3d(
        x=[0, p*0.6, p*0.6, 0, 0], y=[0, 0, l*0.8, l*0.8, 0], z=[0, 0, 0, 0, 0],
        mode='lines', line=dict(color='#2B2D42', width=5), name="Sloof Struktur"
    ))
    # Roof/L2 Ring Balk
    fig.add_trace(go.Scatter3d(
        x=[0, p*0.6, p*0.6, 0, 0], y=[0, 0, l*0.8, l*0.8, 0], z=[h_lantai, h_lantai, h_lantai, h_lantai, h_lantai],
        mode='lines', line=dict(color='#D90429', width=5), name="Ring Balk Atap"
    ))

    # Dinding Solid Bersih (Clean Architectural Massing)
    fig.add_trace(go.Mesh3d(
        x=[0, p*0.6, p*0.6, 0, 0, p*0.6, p*0.6, 0],
        y=[0, 0, l*0.8, l*0.8, 0, 0, l*0.8, l*0.8],
        z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
        i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
        k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
        color='#EDF2F4', opacity=0.85, name="Massa Bangunan"
    ))

    # Atap Frame Teknis
    fig.add_trace(go.Scatter3d(
        x=[0, p*0.3, p*0.6, 0, p*0.3, p*0.6],
        y=[0, (l*0.8)/2, 0, l*0.8, (l*0.8)/2, l*0.8],
        z=[h_lantai, h_lantai+2, h_lantai, h_lantai, h_lantai+2, h_lantai],
        mode='lines', line=dict(color='#8D99AE', width=4), name="Kuda-kuda Atap"
    ))

    # Area Kolam Renang (Garis Blueprint)
    if kolam:
        fig.add_trace(go.Scatter3d(
            x=[p*0.65, p*0.95, p*0.95, p*0.65, p*0.65],
            y=[l*0.1, l*0.1, l*0.7, l*0.7, l*0.1],
            z=[0, 0, 0, 0, 0],
            mode='lines', line=dict(color='#0077B6', width=4), name="Garis Kolam"
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)', backgroundcolor="#FFFFFF", gridcolor="#E5E5E5"),
            yaxis=dict(title='Lebar (m)', backgroundcolor="#FFFFFF", gridcolor="#E5E5E5"),
            zaxis=dict(title='Tinggi (m)', backgroundcolor="#FFFFFF", gridcolor="#E5E5E5"),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.5, y=-1.5, z=1.2))
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=480
    )
    return fig

# -------------------------------------------------------------------
# KALKULASI ENGINEERING & PERHITUNGAN BIUAYA AHSP/SNI
# -------------------------------------------------------------------
def calculate_real_engineering(p, l, jml_lantai, bg_klien, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.6
    luas_bangunan_total = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    # Standar Harga Konstruksi 2026 (Per m2)
    biaya_per_m2 = 4850000 if jml_lantai == 1 else 5850000
    est_konstruksi_rumah = luas_bangunan_total * biaya_per_m2
    
    biaya_kolam = 70000000 if kolam else 0
    total_est_biaya = est_konstruksi_rumah + biaya_kolam
    
    # Material Analisis Harga Satuan Pekerjaan (AHSP)
    keliling_dinding = (p + l) * 2 * jml_lantai * 3.5
    batu_bata = int(keliling_dinding * 70)
    semen_sak = int(luas_bangunan_total * 1.35)
    besi_batang = int(luas_bangunan_total * 2.8)
    cat_kaleng = int((keliling_dinding * 2) / 90) + 1
    
    return luas_tanah, luas_bangunan_total, total_est_biaya, batu_bata, semen_sak, besi_batang, cat_kaleng

# Denah Layout 2D Engineering
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="#111", width=3), fillcolor="#FAFAFA")
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.45, y1=l*0.5, fillcolor="#E2E2E2", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.225], y=[l*0.25], text=["<b>R. Utama & Keluarga</b>"], mode="text"))
    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#D1E7DD", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.65, y1=l, fillcolor="#CFE2FF", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.525], y=[l*0.75], text=["<b>Kamar Anak</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.45, y0=0, x1=p*0.65, y1=l*0.5, fillcolor="#FFF3CD", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.25], text=["<b>Dapur & Service</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.65, y0=0, x1=p, y1=l, fillcolor="#E0F2FE", line=dict(color="#333", width=2))
    fig.add_trace(go.Scatter(x=[p*0.825], y=[l*0.5], text=["<b>Area Outdoor / Kolam</b>"], mode="text"))
    fig.update_xaxes(title="Lebar Lahan (Meter)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang Lahan (Meter)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=20, b=10))
    return fig

# -------------------------------------------------------------------
# DISPLAY OUTPUT
# -------------------------------------------------------------------
with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Pemodelan Arsitektur & Perhitungan RAB Engineering Berhasil!")
            
            lt, lb, est_biaya, bata, semen, besi, cat = calculate_real_engineering(panjang, lebar, lantai, budget, ada_kolam)
            
            tab_render, tab_bim, tab_rab, tab_solusi, tab_2d = st.tabs([
                "📸 Render Realistis Fasad & Interior", 
                "📐 Model 3D BIM Wireframe", 
                "📊 RAB & Material SNI", 
                "💡 Konsultasi & Solusi Klien",
                "🏛️ Denah Layout 2D"
            ])
            
            # --- TAB 1: VISUAL RENDER REALISTIS MANUSIA (STANDAR PRESENTASI) ---
            with tab_render:
                st.subheader("🖼️ Visualisasi Render Fasad & Interior Realistis")
                st.caption("Hasil render visual arsitektur kelas tinggi untuk presentasi ke klien:")
                
                clean_prompt = prompt.replace(" ", "%20")
                gaya_clean = gaya.split(" ")[0].lower()
                
                img_fasad = f"https://image.pollinations.ai/prompt/photorealistic%20architectural%20render%20of%20a%20modern%20{gaya_clean}%20house,%20exterior%20facade,%20{clean_prompt},%20wooden%20door,%20large%20glass%20windows,%20warm%20exterior%20lighting,%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=550&seed=202"
                img_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya_clean}%20style,%20king%20bed,%20ambient%20lighting,%20large%20window?width=512&height=350&seed=303"
                img_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20and%20dining%20area,%20marble%20countertop,%20{gaya_clean}%20style?width=512&height=350&seed=404"
                
                st.image(img_fasad, caption="Render Fasad Eksterior & Lanskap Utama", use_container_width=True)
                
                c_img1, c_img2 = st.columns(2)
                with c_img1:
                    st.image(img_kamar, caption="Konsep Interior Kamar Tidur", use_container_width=True)
                with c_img2:
                    st.image(img_dapur, caption="Konsep Interior Dapur Modern", use_container_width=True)

            # --- TAB 2: MODEL 3D BIM STRUCTURAL WIREFRAME ---
            with tab_bim:
                st.subheader("📐 Model 3D Wireframe & Masa Struktur (BIM)")
                st.caption("Skema grid kolom, ring balk, dan geometri massa bangunan berstandar software CAD/Revit:")
                st.plotly_chart(generate_engineering_3d_bim(panjang, lebar, lantai, ada_kolam), use_container_width=True)

            # --- TAB 3: RAB & PERHITUNGAN BIAYA MATERIAL ---
            with tab_rab:
                st.subheader("📊 Rencana Anggaran Biaya (RAB) & Estimasi Material")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Lahan Tanah", f"{lt} m²")
                m2.metric("Luas Total Bangunan", f"{lb:.1f} m²")
                m3.metric("Estimasi Total Biaya", f"Rp {est_biaya:,.0f}")
                
                st.markdown("---")
                st.write("#### 🧱 Kebutuhan Material Konstruksi Utama (SNI Standard):")
                
                c_mat1, c_mat2 = st.columns(2)
                with c_mat1:
                    st.write(f"- 🧱 **Bata Merah / Hebel:** ± {bata:,} Pcs")
                    st.write(f"- 📦 **Semen Portland (50kg):** ± {semen:,} Sak")
                with c_mat2:
                    st.write(f"- 🏗️ **Besi Beton Structur (10/12mm):** ± {besi:,} Batang")
                    st.write(f"- 🎨 **Cat Dinding (25kg):** ± {cat} Kaleng")

            # --- TAB 4: SOLUSI KONSULTASI UNTUK KONSUMEN ---
            with tab_solusi:
                st.subheader("💡 Analisis Rekomendasi Engineer & Solusi Klien")
                
                selisih_budget = budget - est_biaya
                
                if selisih_budget < 0:
                    st.error(f"⚠️ **Estimasi Konstruksi Melebihi Target Budget (Defisit: Rp {abs(selisih_budget):,.0f})**")
                    st.markdown("### 🛠️ Solusi Engineering & Penghematan Biaya:")
                    st.write("1. **Pembangunan Bertahap (Rumah Tumbuh):** Utamakan penyelesaian struktur utama lantai 1 & atap. Lantai 2 dan pekerjaan *finishing* kolam dapat ditunda ke tahap 2.")
                    st.write("2. **Efisiensi Dinding:** Menggunakan pasangan Dinding Bata Ringan (Hebel) pengganti bata merah untuk menghemat biaya tukang hingga 15%.")
                    st.write("3. **Alternatif Area Luar:** Mengubah kolam renang permanen menjadi *dry garden* / patio terbuka guna menghemat anggaran ± Rp 70.000.000.")
                else:
                    st.success(f"✅ **Budget Klien Terpenuhi (Margin Aman: Rp {selisih_budget:,.0f})**")
                    st.markdown("### 🌟 Rekomendasi Optimalisasi Kualitas Bangunan:")
                    st.write("1. **Peningkatan Finishing:** Sisa anggaran dapat dialokasikan untuk penutup lantai *Granite Tile 80x80cm* dan kusen aluminium *powder coating*.")
                    st.write("2. **Sistem Panel Surya & Smart Home:** Mengintegrasikan panel surya atap dan *smart door lock* untuk efisiensi operasional rumah.")
                    st.write("3. **Lanskap & Lighting Fasad:** Menambahkan pencahayaan arsitektural LED *warm white* pada fasad depan.")

            # --- TAB 5: DENAH 2D ---
            with tab_2d:
                st.subheader("🏛️ Layout Denah Tata Ruang 2D")
                st.plotly_chart(generate_2d_floorplan(panjang, lebar), use_container_width=True)

            st.markdown("---")
            st.download_button(
                label="⬇️ Unduh DXF File Drafter CAD Engine",
                data=generate_dxf_file(panjang, lebar),
                file_name=f"DELUXY_Layout_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan ketikkan deskripsi kebutuhan arsitektur terlebih dahulu.")
