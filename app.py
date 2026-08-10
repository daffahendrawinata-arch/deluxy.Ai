import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & BRANDING
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Architectural & Engineering Platform", 
    page_icon="🏛️", 
    layout="wide"
)

st.title("🏛️ DELUXY.Ai - AI Architectural & Civil Engineering Engine")
st.markdown("##### *Lead Engineer & Developer: **Daffa Hendrawinata***")
st.caption("Platform Pemodelan 3D Arsitektur, Analisis Struktur RAB AHSP, dan Modul Konsultasi Strategis Klien")
st.markdown("---")

# -------------------------------------------------------------------
# INPUT PARAMETER
# -------------------------------------------------------------------
col_input, col_output = st.columns([1, 2.2])

with col_input:
    st.subheader("⚙️ Parameter Desain & Budget Klien")
    
    prompt = st.text_area(
        "Konsep & Kebutuhan Spesifik Klien:", 
        placeholder="Contoh: Rumah 2 lantai minimalis modern budget 600jt, 3 kamar tidur, bukaan kaca lebar, ada kolam renang",
        height=100
    )
    
    budget = st.number_input("Target Budget Klien (Rp):", min_value=100000000, value=600000000, step=25000000, format="%d")
    gaya = st.selectbox("Gaya Fasad Arsitektur:", [
        "Minimalis Modern (Clean Glass & Wood)", 
        "Skandinavia / Japandi (Warm Earthy & White)", 
        "Mewah Kontemporer (Luxury Marble & Concrete)", 
        "Industrial Modern (Exposed Brick & Black Steel)"
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
# ENGINE MODEL 3D DENGAN LIGHTING & TEXTURED MATERIAL (NON-FLAT)
# -------------------------------------------------------------------
def add_3d_block(fig, x0, x1, y0, y1, z0, z1, color, opacity=1.0, name=""):
    x = [x0, x1, x1, x0, x0, x1, x1, x0]
    y = [y0, y0, y1, y1, y0, y0, y1, y1]
    z = [z0, z0, z0, z0, z1, z1, z1, z1]
    i = [7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]
    j = [3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6]
    k = [0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2]
    
    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k,
        color=color,
        opacity=opacity,
        lighting=dict(ambient=0.6, diffuse=0.8, fresnel=0.3, specular=0.5, roughness=0.4),
        lightposition=dict(x=100, y=200, z=300),
        name=name, showlegend=False
    ))

def generate_textured_3d_model(p, l, jml_lantai, kolam):
    fig = go.Figure()
    h_total = 3.6 * jml_lantai

    # 1. Base Ground & Rumput Lanskap
    add_3d_block(fig, -2, p+2, -2, l+2, -0.2, 0.0, '#386641', name="Rumput Taman")
    
    # 2. Carport / Hardscape (Texture Concrete)
    add_3d_block(fig, 0, p*0.35, -1.8, 0.0, 0.0, 0.08, '#8D99AE', name="Carport")

    # 3. Podium & Floor Base
    add_3d_block(fig, 0, p*0.65, 0, l*0.8, 0.0, 0.2, '#E9ECEF', name="Pedestal")

    # 4. Dinding Utama (Off-White Architecture Material)
    add_3d_block(fig, 0, p*0.65, 0, l*0.8, 0.2, h_total, '#F8F9FA', opacity=0.98, name="Dinding Utama")

    # 5. Accent Wall Wood/Stone Fasad Depan
    add_3d_block(fig, p*0.22, p*0.65, -0.04, 0.02, 0.2, h_total, '#6C584C', name="Panel Kayu Fasad")

    # 6. Pintu Utama (Kusen Frame + Daun Pintu Kayu + Gagang Metal)
    add_3d_block(fig, p*0.06, p*0.18, -0.05, 0.02, 0.2, 2.4, '#2B1B17', name="Kusen Pintu")
    add_3d_block(fig, p*0.07, p*0.17, -0.06, -0.01, 0.2, 2.35, '#A77464', name="Daun Pintu Kayu")
    add_3d_block(fig, p*0.15, p*0.16, -0.09, -0.05, 1.1, 1.3, '#D4AF37', name="Gagang Pintu")

    # 7. Jendela Fasad Kaca & Kusen Black Aluminum
    # Frame Utama
    add_3d_block(fig, p*0.25, p*0.58, -0.05, 0.02, 0.8, h_total*0.75, '#1A1A1A', name="Kusen Jendela")
    # Kaca Transparan dengan Lighting Specular
    add_3d_block(fig, p*0.26, p*0.57, -0.06, -0.01, 0.85, h_total*0.73, '#00B4D8', opacity=0.55, name="Kaca Transparan")
    # Vertical Mullion
    add_3d_block(fig, p*0.41, p*0.42, -0.07, -0.01, 0.85, h_total*0.73, '#1A1A1A', name="Mullion Frame")

    # 8. Detail Lantai 2 & Canopy Minimalis
    if jml_lantai == 2:
        # Canopy Pembatas Lantai
        add_3d_block(fig, -0.2, p*0.67, -0.4, 0.4, 3.5, 3.65, '#212529', name="Canopy Lantai 2")
        # Balkon Kaca
        add_3d_block(fig, p*0.05, p*0.6, -0.35, -0.3, 3.65, 4.4, '#4EA8DE', opacity=0.4, name="Balkon Kaca")
        add_3d_block(fig, p*0.05, p*0.6, -0.37, -0.28, 4.38, 4.45, '#212529', name="Railing Top Bar")

    # 9. Atap Limas Modern Bertekstur
    x_roof = [0, p*0.65, p*0.65, 0, (p*0.65)/2]
    y_roof = [0, 0, l*0.8, l*0.8, (l*0.8)/2]
    z_roof = [h_total, h_total, h_total, h_total, h_total + 2.2]
    fig.add_trace(go.Mesh3d(
        x=x_roof, y=y_roof, z=z_roof,
        i=[0,1,2,3], j=[1,2,3,0], k=[4,4,4,4],
        color='#3D5A80', opacity=1.0,
        lighting=dict(ambient=0.5, diffuse=0.9, fresnel=0.2),
        name="Atap Modern"
    ))

    # 10. Area Kolam Renang & Lanskap Outdoor
    if kolam:
        # Pool Deck Kayu
        add_3d_block(fig, p*0.68, p*0.96, 0, l*0.8, 0.0, 0.1, '#D4A373', name="Deck Kayu")
        # Keramik Kolam
        add_3d_block(fig, p*0.72, p*0.92, l*0.12, l*0.68, -0.8, 0.0, '#0077B6', name="Dinding Kolam")
        # Air Kolam (Transparan & Reflective)
        add_3d_block(fig, p*0.725, p*0.915, l*0.13, l*0.67, -0.7, -0.05, '#48CAE4', opacity=0.75, name="Air Kolam")

    # Camera & Ambient Setup
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            yaxis=dict(title='Lebar (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            zaxis=dict(title='Tinggi (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.6, y=-1.6, z=1.2))
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=520
    )
    return fig

# -------------------------------------------------------------------
# ENGINE KALKULASI RAB DETAIL & MATERIAL AHSP SNI
# -------------------------------------------------------------------
def calculate_engineering_rab(p, l, jml_lantai, bg_klien, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.6
    luas_bangunan_total = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    # Standar Harga Satuan Konstruksi Bangunan (2026)
    harga_m2_struktural = 4900000 if jml_lantai == 1 else 5900000
    est_bangunan_utama = luas_bangunan_total * harga_m2_struktural
    biaya_kolam = 75000000 if kolam else 0
    total_est_biaya = est_bangunan_utama + biaya_kolam

    # Breakdown Pekerjaan RAB
    p_persiapan = total_est_biaya * 0.05
    p_struktur = total_est_biaya * 0.38
    p_dinding_finishing = total_est_biaya * 0.32
    p_atap = total_est_biaya * 0.13
    p_mep = total_est_biaya * 0.12

    # Quantitas Material AHSP SNI
    keliling_dinding = (p + l) * 2 * jml_lantai * 3.6
    batu_bata = int(keliling_dinding * 70)
    semen_sak = int(luas_bangunan_total * 1.35)
    besi_batang = int(luas_bangunan_total * 2.8)
    cat_kaleng = int((keliling_dinding * 2) / 90) + 1
    
    return {
        'luas_tanah': luas_tanah,
        'luas_bangunan': luas_bangunan_total,
        'total_biaya': total_est_biaya,
        'p_persiapan': p_persiapan,
        'p_struktur': p_struktur,
        'p_dinding_finishing': p_dinding_finishing,
        'p_atap': p_atap,
        'p_mep': p_mep,
        'batu_bata': batu_bata,
        'semen_sak': semen_sak,
        'besi_batang': besi_batang,
        'cat_kaleng': cat_kaleng
    }

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

def generate_dxf_file(p, l):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0,0), (p,0), (p,l), (0,l), (0,0)], dxfattribs={"layer": "DINDING_LUAR"})
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

# -------------------------------------------------------------------
# DISPLAY OUTPUT
# -------------------------------------------------------------------
with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Pemodelan 3D & Kalkulasi Engineering RAB Berhasil Disusun!")
            
            rab = calculate_engineering_rab(panjang, lebar, lantai, budget, ada_kolam)
            
            tab_3d, tab_render, tab_rab, tab_solusi, tab_2d = st.tabs([
                "🏠 Model 3D Textured & Lighting", 
                "📸 Render Realistis Arsitektur", 
                "📊 Breakdown RAB & Material SNI", 
                "💡 Konsultasi Strategis Klien",
                "🏛️ Layout Denah 2D"
            ])
            
            # --- TAB 1: MODEL 3D TEXTURED (TIDAK FLAT) ---
            with tab_3d:
                st.subheader("🏠 Model 3D Interaktif (Material & Depth Effect)")
                st.caption("Model 3D dilengkapi shading, efek kedalaman, kaca transparan, dan detail kusen arsitektural:")
                st.plotly_chart(generate_textured_3d_model(panjang, lebar, lantai, ada_kolam), use_container_width=True)

            # --- TAB 2: RENDER FOTO REALISTIS ---
            with tab_render:
                st.subheader("🖼️ Render Visual Realistis Kelas Presentasi")
                st.caption("Visualisasi pencahayaan dan finishing material bangunan asli berdasarkan konsep input:")
                
                clean_prompt = prompt.replace(" ", "%20")
                gaya_clean = gaya.split(" ")[0].lower()
                
                img_fasad = f"https://image.pollinations.ai/prompt/photorealistic%20architectural%20render%20of%20a%20modern%20{gaya_clean}%20house,%20exterior%20facade,%20{clean_prompt},%20wooden%20door,%20large%20glass%20windows,%20warm%20lighting,%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=550&seed=505"
                img_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya_clean}%20style,%20king%20bed,%20ambient%20lighting,%20large%20window?width=512&height=350&seed=606"
                img_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20and%20dining%20area,%20marble%20countertop,%20{gaya_clean}%20style?width=512&height=350&seed=707"
                
                st.image(img_fasad, caption="Fasad Eksterior Hasil Render AI", use_container_width=True)
                
                c_img1, c_img2 = st.columns(2)
                with c_img1:
                    st.image(img_kamar, caption="Interior Kamar Tidur Utama", use_container_width=True)
                with c_img2:
                    st.image(img_dapur, caption="Interior Dapur & Dining Area", use_container_width=True)

            # --- TAB 3: BREAKDOWN RAB TEKNIS & MATERIAL ---
            with tab_rab:
                st.subheader("📊 Rencana Anggaran Biaya (RAB) & Volume Material")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Lahan Tanah", f"{rab['luas_tanah']} m²")
                m2.metric("Luas Total Bangunan", f"{rab['luas_bangunan']:.1f} m²")
                m3.metric("Estimasi Total RAB", f"Rp {rab['total_biaya']:,.0f}")
                
                st.markdown("---")
                st.write("#### 🏗️ Breakdown Pembagian Biaya Pekerjaan:")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.write(f"- 📄 **Pekerjaan Persiapan & Fondasi (5%):** Rp {rab['p_persiapan']:,.0f}")
                    st.write(f"- 🏗️ **Pekerjaan Struktur Beton & Beton (38%):** Rp {rab['p_struktur']:,.0f}")
                    st.write(f"- 🧱 **Pekerjaan Dinding & Finishing (32%):** Rp {rab['p_dinding_finishing']:,.0f}")
                with col_b2:
                    st.write(f"- 🏠 **Pekerjaan Rangka & Atap (13%):** Rp {rab['p_atap']:,.0f}")
                    st.write(f"- ⚡ **Pekerjaan MEP & Sanitasi (12%):** Rp {rab['p_mep']:,.0f}")

                st.markdown("---")
                st.write("#### 📦 Estimasi Kebutuhan Material Utama (AHSP Standard):")
                c_mat1, c_mat2 = st.columns(2)
                with c_mat1:
                    st.write(f"- 🧱 **Bata Merah / Hebel:** ± {rab['batu_bata']:,} Pcs")
                    st.write(f"- 📦 **Semen Portland (50kg):** ± {rab['semen_sak']:,} Sak")
                with c_mat2:
                    st.write(f"- 🏗️ **Besi Beton Structur (10/12mm):** ± {rab['besi_batang']:,} Batang")
                    st.write(f"- 🎨 **Cat Dinding Exterior/Interior (25kg):** ± {rab['cat_kaleng']} Kaleng")

            # --- TAB 4: MODUL KONSULTASI STRATEGIS KLIEN ---
            with tab_solusi:
                st.subheader("💡 Analysis & Advisory Konsultasi Klien")
                
                selisih_budget = budget - rab['total_biaya']
                
                if selisih_budget < 0:
                    st.error(f"⚠️ **Estimasi Konstruksi Melebihi Target Budget Klien (Defisit: Rp {abs(selisih_budget):,.0f})**")
                    st.markdown("### 🛠️ Poin Rekomendasi Konsultasi ke Klien (Skenario Defisit):")
                    st.write("1. **Skema Rumah Tumbuh:** Sarankan ke klien untuk memprioritaskan penyelesaian struktur lantai 1 & atap terlebih dahulu. Lantai 2 / finishing kolam renang dialokasikan ke pembangunan tahap berikutnya.")
                    st.write("2. **Substitusi Material Dinding:** Berikan opsi bata ringan (Hebel) pengganti bata merah konvensional untuk memangkas durasi serta biaya tenaga kerja hingga 15%.")
                    st.write("3. **Rasionalisasi Kolam Renang:** Alihkan fasilitas kolam renang ke *patio / dry garden* modern untuk menghemat dana sebesar ± Rp 75.000.000.")
                else:
                    st.success(f"✅ **Budget Klien Mencukupi (Sisa Margin: Rp {selisih_budget:,.0f})**")
                    st.markdown("### 🌟 Poin Rekomendasi Konsultasi ke Klien (Skenario Optimal):")
                    st.write("1. **Upgrade Spesifikasi Finishing:** Alokasikan sisa margin untuk mengupgrade lantai dari keramik biasa ke *Granite Tile 80x80cm* serta kusen aluminium *powder coating*.")
                    st.write("2. **Integrasi Smart Home & Energy Saving:** Tawarkan penambahan sistem kunci pintu otomatis (*Smart Lock*), sakelar pintar, dan panel surya atap.")
                    st.write("3. **Lanskap & Lighting Fasad:** Lengkapi bagian luar dengan sistem pencahayaan sorot arsitektural (*Warm White LED*) untuk menaikkan nilai estetika properti.")

            # --- TAB 5: DENAH LAYOUT 2D ---
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
            st.warning("Silakan ketikkan deskripsi konsep impian terlebih dahulu.")
