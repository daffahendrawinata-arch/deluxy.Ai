import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & CUSTOM CSS (UI ELEGAN & NON-FLAT)
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Architectural & Engineering Platform", 
    page_icon="🏛️", 
    layout="wide"
)

# Custom CSS Inject untuk mempercantik UI Streamlit agar tidak kaku/flat
st.markdown("""
    <style>
    /* Gradient Background untuk Header */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    /* Styling Card Container */
    .stCard {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    
    /* Tombol Generate Custom Gradient */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border-radius: 8px;
        font-weight: 600;
        height: 48px;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown("""
    <div class="main-header">
        <h1 style="margin:0; font-size: 2.2rem;">🏛️ DELUXY.Ai Engine</h1>
        <p style="margin-top: 5px; opacity: 0.8; font-size: 1rem;">Architectural 3D Modeling, Structural RAB Engineering, & Strategic Client Advisory</p>
        <p style="margin-top: 10px; font-weight: 600; color: #38bdf8;">Lead Engineer & Developer: Daffa Hendrawinata</p>
    </div>
""", unsafe_allow_html=True)

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
# ENGINE MODEL 3D DENGAN LIGHTING & TEXTURED MATERIAL
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
        lighting=dict(ambient=0.65, diffuse=0.85, fresnel=0.3, specular=0.5, roughness=0.35),
        lightposition=dict(x=150, y=200, z=300),
        name=name, showlegend=False
    ))

def generate_textured_3d_model(p, l, jml_lantai, kolam):
    fig = go.Figure()
    h_total = 3.6 * jml_lantai

    # Base Ground & Rumput Lanskap
    add_3d_block(fig, -2, p+2, -2, l+2, -0.2, 0.0, '#386641', name="Rumput Taman")
    
    # Carport
    add_3d_block(fig, 0, p*0.35, -1.8, 0.0, 0.0, 0.08, '#8D99AE', name="Carport")

    # Pedestal Utama
    add_3d_block(fig, 0, p*0.65, 0, l*0.8, 0.0, 0.2, '#E9ECEF', name="Pedestal")

    # Dinding Utama
    add_3d_block(fig, 0, p*0.65, 0, l*0.8, 0.2, h_total, '#F8F9FA', opacity=0.98, name="Dinding Utama")

    # Panel Fasad
    add_3d_block(fig, p*0.22, p*0.65, -0.04, 0.02, 0.2, h_total, '#6C584C', name="Panel Kayu Fasad")

    # Pintu Utama & Detail Kusen
    add_3d_block(fig, p*0.06, p*0.18, -0.05, 0.02, 0.2, 2.4, '#2B1B17', name="Kusen Pintu")
    add_3d_block(fig, p*0.07, p*0.17, -0.06, -0.01, 0.2, 2.35, '#A77464', name="Daun Pintu Kayu")
    add_3d_block(fig, p*0.15, p*0.16, -0.09, -0.05, 1.1, 1.3, '#D4AF37', name="Gagang Pintu")

    # Jendela Kaca Depan
    add_3d_block(fig, p*0.25, p*0.58, -0.05, 0.02, 0.8, h_total*0.75, '#1A1A1A', name="Kusen Jendela")
    add_3d_block(fig, p*0.26, p*0.57, -0.06, -0.01, 0.85, h_total*0.73, '#00B4D8', opacity=0.55, name="Kaca Transparan")

    # Detail Lantai 2 (Jikalau 2 lantai)
    if jml_lantai == 2:
        add_3d_block(fig, -0.2, p*0.67, -0.4, 0.4, 3.5, 3.65, '#212529', name="Canopy Lantai 2")
        add_3d_block(fig, p*0.05, p*0.6, -0.35, -0.3, 3.65, 4.4, '#4EA8DE', opacity=0.4, name="Balkon Kaca")

    # Atap Limas Modern
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

    # Kolam Renang
    if kolam:
        add_3d_block(fig, p*0.68, p*0.96, 0, l*0.8, 0.0, 0.1, '#D4A373', name="Deck Kayu")
        add_3d_block(fig, p*0.72, p*0.92, l*0.12, l*0.68, -0.8, 0.0, '#0077B6', name="Dinding Kolam")
        add_3d_block(fig, p*0.725, p*0.915, l*0.13, l*0.67, -0.7, -0.05, '#48CAE4', opacity=0.75, name="Air Kolam")

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            yaxis=dict(title='Lebar (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            zaxis=dict(title='Tinggi (m)', backgroundcolor="#F8F9FA", gridcolor="#E5E5E5"),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.6, y=-1.6, z=1.2))
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=500
    )
    return fig

# -------------------------------------------------------------------
# ENGINE KALKULASI RAB DETAIL & MATERIAL AHSP SNI
# -------------------------------------------------------------------
def calculate_engineering_rab(p, l, jml_lantai, bg_klien, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.6
    luas_bangunan_total = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    harga_m2_struktural = 4900000 if jml_lantai == 1 else 5900000
    est_bangunan_utama = luas_bangunan_total * harga_m2_struktural
    biaya_kolam = 75000000 if kolam else 0
    total_est_biaya = est_bangunan_utama + biaya_kolam

    return {
        'luas_tanah': luas_tanah,
        'luas_bangunan': luas_bangunan_total,
        'total_biaya': total_est_biaya,
        'p_persiapan': total_est_biaya * 0.05,
        'p_struktur': total_est_biaya * 0.38,
        'p_dinding_finishing': total_est_biaya * 0.32,
        'p_atap': total_est_biaya * 0.13,
        'p_mep': total_est_biaya * 0.12,
        'batu_bata': int((p + l) * 2 * jml_lantai * 3.6 * 70),
        'semen_sak': int(luas_bangunan_total * 1.35),
        'besi_batang': int(luas_bangunan_total * 2.8),
        'cat_kaleng': int((((p + l) * 2 * jml_lantai * 3.6) * 2) / 90) + 1
    }

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
# DISPLAY OUTPUT & GALLERY REFERENSI REALISTIS
# -------------------------------------------------------------------
with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Pemodelan 3D & Kalkulasi Engineering RAB Berhasil Disusun!")
            
            rab = calculate_engineering_rab(panjang, lebar, lantai, budget, ada_kolam)
            
            tab_3d, tab_gallery, tab_rab, tab_solusi, tab_2d = st.tabs([
                "🏠 Model 3D Structural", 
                "🖼️ Moodboard & Referensi Desain", 
                "📊 Breakdown RAB & Material SNI", 
                "💡 Konsultasi Strategis Klien",
                "🏛️ Layout Denah 2D"
            ])
            
            # --- TAB 1: MODEL 3D INTERAKTIF ---
            with tab_3d:
                st.subheader("🏠 Model 3D Massing & Fasad")
                st.caption("Gunakan mouse untuk merotasi, memperbesar, dan melihat posisi bukaan serta struktur:")
                st.plotly_chart(generate_textured_3d_model(panjang, lebar, lantai, ada_kolam), use_container_width=True)

            # --- TAB 2: REFERENSI MOODBOARD INTERIOR & EKSTERIOR (UNSPLASH ARCHITECTURE) ---
            with tab_gallery:
                st.subheader("🖼️ Konsep Referensi Arsitektur & Interior Pilihan")
                st.caption("Koleksi referensi desain nyata beresolusi tinggi untuk disajikan kepada konsumen:")
                
                # Fasad Utama
                st.markdown("#### 1. Referensi Fasad Eksterior Modern")
                st.image(
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80", 
                    caption="Konsep Fasad Minimalis Modern - Penggabungan Elemen Kayu, Kaca, & Beton", 
                    use_container_width=True
                )
                
                st.markdown("---")
                
                # Interior Kamar Tidur & Dapur (Side by Side)
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    st.markdown("#### 2. Konsep Kamar Tidur Utama")
                    st.image(
                        "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80", 
                        caption="Kamar Tidur Utama - Warm Wood Backlight & Ambient Lighting", 
                        use_container_width=True
                    )
                
                with col_g2:
                    st.markdown("#### 3. Konsep Dapur & Dining Area")
                    st.image(
                        "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80", 
                        caption="Dapur Modern - Island Table & Finished Marble Top", 
                        use_container_width=True
                    )

            # --- TAB 3: BREAKDOWN RAB ---
            with tab_rab:
                st.subheader("📊 Rencana Anggaran Biaya (RAB) & Volume Material")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Lahan Tanah", f"{rab['luas_tanah']} m²")
                m2.metric("Luas Total Bangunan", f"{rab['luas_bangunan']:.1f} m²")
                m3.metric("Estimasi Total RAB", f"Rp {rab['total_biaya']:,.0f}")
                
                st.markdown("---")
                st.write("#### 🏗️ Breakdown Biaya Pekerjaan:")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    st.write(f"- 📄 **Persiapan & Fondasi (5%):** Rp {rab['p_persiapan']:,.0f}")
                    st.write(f"- 🏗️ **Pekerjaan Struktur (38%):** Rp {rab['p_struktur']:,.0f}")
                    st.write(f"- 🧱 **Dinding & Finishing (32%):** Rp {rab['p_dinding_finishing']:,.0f}")
                with col_b2:
                    st.write(f"- 🏠 **Atap & Kuda-kuda (13%):** Rp {rab['p_atap']:,.0f}")
                    st.write(f"- ⚡ **MEP & Sanitasi (12%):** Rp {rab['p_mep']:,.0f}")

                st.markdown("---")
                st.write("#### 📦 Volume Material Utama (AHSP Standard):")
                c_mat1, c_mat2 = st.columns(2)
                with c_mat1:
                    st.write(f"- 🧱 **Bata Merah / Hebel:** ± {rab['batu_bata']:,} Pcs")
                    st.write(f"- 📦 **Semen Portland (50kg):** ± {rab['semen_sak']:,} Sak")
                with c_mat2:
                    st.write(f"- 🏗️ **Besi Beton Structur (10/12mm):** ± {rab['besi_batang']:,} Batang")
                    st.write(f"- 🎨 **Cat Dinding (25kg):** ± {rab['cat_kaleng']} Kaleng")

            # --- TAB 4: KONSULTASI KLIEN ---
            with tab_solusi:
                st.subheader("💡 Analysis & Advisory Konsultasi Klien")
                
                selisih_budget = budget - rab['total_biaya']
                
                if selisih_budget < 0:
                    st.error(f"⚠️ **Estimasi Konstruksi Melebihi Target Budget Klien (Defisit: Rp {abs(selisih_budget):,.0f})**")
                    st.markdown("### 🛠️ Poin Rekomendasi Konsultasi ke Klien (Skenario Defisit):")
                    st.write("1. **Skema Rumah Tumbuh:** Sarankan ke klien untuk memprioritaskan penyelesaian struktur lantai 1 & atap terlebih dahulu. Lantai 2 / finishing kolam renang dialokasikan ke tahap berikutnya.")
                    st.write("2. **Substitusi Material Dinding:** Gunakan bata ringan (Hebel) untuk memangkas durasi serta biaya tukang hingga 15%.")
                    st.write("3. **Rasionalisasi Kolam Renang:** Alihkan area kolam renang ke *dry garden* modern untuk menghemat anggaran ± Rp 75.000.000.")
                else:
                    st.success(f"✅ **Budget Klien Mencukupi (Sisa Margin: Rp {selisih_budget:,.0f})**")
                    st.markdown("### 🌟 Poin Rekomendasi Konsultasi ke Klien (Skenario Surplus):")
                    st.write("1. **Upgrade Finishing:** Gunakan sisa margin untuk mengupgrade penutup lantai ke *Granite Tile 80x80cm* serta kusen aluminium *powder coating*.")
                    st.write("2. **Smart Home Integration:** Tawarkan penambahan sistem kunci pintu otomatis (*Smart Lock*) dan panel surya atap.")
                    st.write("3. **Lanskap & Lighting:** Tambahkan lighting sorot arsitektural (*Warm White*) untuk fasad malam hari.")

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
            st.warning("Silakan ketikkan deskripsi konsep impian terlebih dahulu.")
        
