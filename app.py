import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & ATRIBUSI PENCIPTA
# -------------------------------------------------------------------
# BISA DIUBAH: Ganti nama Anda di bawah ini
NAMA_PENCIPTA = "Muhammad Daffa Hendra WInata, CPS, s.T" 

st.set_page_config(
    page_title=f"DELUXY.Ai by {NAMA_PENCIPTA}", 
    page_icon="🏛️", 
    layout="wide"
)

# Custom Styling CSS
st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        border-left: 6px solid #38b000;
    }}
    .creator-badge {{
        background-color: #38b000;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 18px;
        background-color: #f1f5f9;
        border-radius: 8px;
        font-weight: 600;
    }}
    .footer-text {{
        text-align: center;
        padding: 20px;
        color: #64748b;
        font-size: 0.9em;
        border-top: 1px solid #e2e8f0;
        margin-top: 40px;
    }}
    </style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown(f"""
    <div class="main-header">
        <h2 style="margin:0;">🏛️ DELUXY.Ai - Architectural & RAB Engine</h2>
        <div class="creator-badge">Created & Designed by {NAMA_PENCIPTA}</div>
        <p style="margin-top: 10px; opacity: 0.85; margin-bottom:0;">
            Platform Pemodelan Lahan, Visualisasi Render Fasad 3D Presisi, & Kalkulasi Engine RAB
        </p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# INPUT PARAMETER (SIDEBAR)
# -------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parameter Klien")
    prompt = st.text_area("Konsep Desain:", "Rumah 2 lantai minimalis modern bukaan kaca lebar, ada kolam renang")
    budget = st.number_input("Target Budget Klien (Rp):", min_value=100000000, value=750000000, step=50000000, format="%d")
    
    st.subheader("Ukuran Lahan")
    panjang = st.slider("Panjang Lahan (m):", 10, 30, 15)
    lebar = st.slider("Lebar Lahan (m):", 6, 20, 8)
    lantai = st.radio("Jumlah Lantai:", [1, 2])
    ada_kolam = st.checkbox("Fasilitas Kolam Renang", value=True)
    
    gaya = st.selectbox("Gaya Fasad Arsitektur:", [
        "Minimalis Modern", 
        "Japandi / Skandinavia", 
        "Industrial Modern", 
        "Mewah Kontemporer"
    ])
    
    btn_generate = st.button("🚀 Hasilkan Visual & Engine RAB", use_container_width=True)

# -------------------------------------------------------------------
# DATABASE VISUAL RENDER 3D RAPI & PRESISI
# -------------------------------------------------------------------
def get_visual_renders(bg, jml_lantai, gaya_pilihan, kolam):
    """Mengambil koleksi gambar render 3D realistis beresolusi tinggi."""
    
    # 1. Gambar Fasad Utama berdasarkan Skenario Gaya & Budget
    if bg >= 800000000 or "Mewah" in gaya_pilihan:
        fasad_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1400&q=80"
        fasad_desc = "Visual Fasad Luxury Modern Glass Box dengan Pencahayaan Warm LED Ambient"
    elif jml_lantai == 2 or bg >= 500000000:
        if "Japandi" in gaya_pilihan:
            fasad_url = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1400&q=80"
            fasad_desc = "Visual Fasad Japandi 2 Lantai - Timber Cladding & Clean White Exterior"
        elif "Industrial" in gaya_pilihan:
            fasad_url = "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1400&q=80"
            fasad_desc = "Visual Fasad Industrial Modern - Exposed Concrete & Steel Frame"
        else:
            fasad_url = "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1400&q=80"
            fasad_desc = "Visual Fasad Minimalis Modern 2 Lantai - Geometris Rapi & Balkon Kaca"
    else:
        fasad_url = "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1400&q=80"
        fasad_desc = "Visual Fasad Compact Minimalis 1 Lantai - Efisiensi Maksimal"

    # 2. Gambar Interior & Area Outdoor
    interior_kamar = "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80"
    interior_dapur = "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80"
    
    if kolam:
        outdoor_url = "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=1200&q=80"
        outdoor_desc = "Visual Backyard Pool & Decking Kayu Minimalis"
    else:
        outdoor_url = "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1200&q=80"
        outdoor_desc = "Visual Taman Belakang / Tropical Inner Courtyard"

    return {
        'fasad_url': fasad_url, 'fasad_desc': fasad_desc,
        'kamar_url': interior_kamar, 'dapur_url': interior_dapur,
        'outdoor_url': outdoor_url, 'outdoor_desc': outdoor_desc
    }

# -------------------------------------------------------------------
# MODEL DIAGRAM TAPAK LAHAN 3D
# -------------------------------------------------------------------
def generate_site_3d_box(p, l, jml_lantai, kolam):
    fig = go.Figure()
    
    # Tapak Lahan
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[-0.1, -0.1, -0.1, -0.1, 0, 0, 0, 0],
        i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
        k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
        color='#38b000', opacity=0.8, name="Batas Lahan Tanah"
    ))
    
    # Massa Bangunan Utama
    tinggi = 3.5 if jml_lantai == 1 else 6.5
    fig.add_trace(go.Mesh3d(
        x=[1, p*0.6, p*0.6, 1, 1, p*0.6, p*0.6, 1],
        y=[1, 1, l*0.8, l*0.8, 1, 1, l*0.8, l*0.8],
        z=[0, 0, 0, 0, tinggi, tinggi, tinggi, tinggi],
        i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
        k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
        color='#48cae4', opacity=0.7, name="Massa Bangunan"
    ))

    # Massa Kolam Renang
    if kolam:
        fig.add_trace(go.Mesh3d(
            x=[p*0.65, p*0.95, p*0.95, p*0.65, p*0.65, p*0.95, p*0.95, p*0.65],
            y=[1, 1, l*0.7, l*0.7, 1, 1, l*0.7, l*0.7],
            z=[-0.4, -0.4, -0.4, -0.4, 0, 0, 0, 0],
            i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
            j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
            k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
            color='#0077b6', opacity=0.9, name="Area Kolam Renang"
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang Lahan (m)'),
            yaxis=dict(title='Lebar Lahan (m)'),
            zaxis=dict(title='Tinggi Bangunan (m)'),
            aspectmode='data'
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=420
    )
    return fig

# -------------------------------------------------------------------
# ENGINE KALKULASI RAB & MATERIAL
# -------------------------------------------------------------------
def hitung_rab(p, l, jml_lantai, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.55
    luas_bangunan = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    biaya_m2 = 4800000 if jml_lantai == 1 else 5800000
    est_bangunan = luas_bangunan * biaya_m2
    biaya_kolam = 75000000 if kolam else 0
    total_rab = est_bangunan + biaya_kolam
    
    return {
        'luas_tanah': luas_tanah,
        'luas_bangunan': luas_bangunan,
        'total_rab': total_rab,
        'hebel_m3': int(luas_bangunan * 0.22),
        'semen_sak': int(luas_bangunan * 1.25),
        'besi_batang': int(luas_bangunan * 2.5)
    }

def generate_dxf(p, l):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0,0), (p,0), (p,l), (0,l), (0,0)], dxfattribs={"layer": "DINDING_OUTER"})
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

# -------------------------------------------------------------------
# MAIN DISPLAY TABS
# -------------------------------------------------------------------
if prompt:
    rab = hitung_rab(panjang, lebar, lantai, ada_kolam)
    visuals = get_visual_renders(budget, lantai, gaya, ada_kolam)
    
    tab_render, tab_site, tab_rab, tab_advis = st.tabs([
        "🖼️ Render Fasad 3D Rapi", 
        "📐 Diagram Plot Tapak Lahan", 
        "📊 RAB & Material Engineering", 
        "💡 Konsultasi Strategis Klien"
    ])
    
    # --- TAB 1: VISUAL RENDER 3D RAPI & DETAIL ---
    with tab_render:
        st.subheader("🖼️ Referensi Render Fasad 3D & Interior Realistis")
        st.caption(f"Visualisasi presisi berbasis preferensi desain oleh **{NAMA_PENCIPTA}**:")
        
        # Gambar Fasad Utama beresolusi tinggi
        st.image(visuals['fasad_url'], caption=visuals['fasad_desc'], use_container_width=True)
        st.markdown("---")
        
        # Interior Grid
        c1, c2, c3 = st.columns(3)
        with c1:
            st.image(visuals['kamar_url'], caption="Kamar Utama - Modern Ambient Lighting", use_container_width=True)
        with c2:
            st.image(visuals['dapur_url'], caption="Dapur & Dining Area - Clean Minimalist", use_container_width=True)
        with c3:
            st.image(visuals['outdoor_url'], caption=visuals['outdoor_desc'], use_container_width=True)

    # --- TAB 2: DIAGRAM SITE LAHAN ---
    with tab_site:
        st.subheader("📐 Pemodelan Orientasi Massa & Tapak Lahan")
        st.caption("Proposi massa bangunan terhadap total luas tanah:")
        st.plotly_chart(generate_site_3d_box(panjang, lebar, lantai, ada_kolam), use_container_width=True)

    # --- TAB 3: BREAKDOWN RAB & MATERIAL ---
    with tab_rab:
        st.subheader("📊 Rencana Anggaran Biaya (RAB) & Material Structur")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Luas Lahan", f"{rab['luas_tanah']} m²")
        k2.metric("Estimasi Luas Bangunan", f"{rab['luas_bangunan']:.1f} m²")
        k3.metric("Estimasi Total RAB", f"Rp {rab['total_rab']:,.0f}")
        
        st.markdown("---")
        st.write("#### 🧱 Estimasi Kebutuhan Material Utama:")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write(f"- **Bata Ringan / Hebel:** ± {rab['hebel_m3']} m³")
            st.write(f"- **Semen Sak (50kg):** ± {rab['semen_sak']} Sak")
        with col_m2:
            st.write(f"- **Besi Beton Structur:** ± {rab['besi_batang']} Batang")

    # --- TAB 4: ADVIS KONSULTASI ---
    with tab_advis:
        st.subheader("💡 Analysis & Strategic Advisory")
        selisih = budget - rab['total_rab']
        
        if selisih < 0:
            st.error(f"⚠️ **Estimasi RAB Melebihi Budget Klien (Defisit: Rp {abs(selisih):,.0f})**")
            st.write("**Opsi Solusi Strategis:**")
            st.write("1. Terapkan konsep **Rumah Tumbuh** (Prioritaskan struktur dan Lantai 1 dulu).")
            st.write("2. Alihkan area kolam renang ke *Taman Tropis Kering* untuk hemat anggaran ± Rp 75 Juta.")
        else:
            st.success(f"✅ **Budget Klien Sangat Mencukupi (Sisa: Rp {selisih:,.0f})**")
            st.write("**Opsi Solusi Strategis:**")
            st.write("1. Alokasikan sisa anggaran untuk *Upgrade Material Granite Tile 80x80cm* atau instalasi *Smart Home System*.")

    st.markdown("---")
    st.download_button(
        label="⬇️ Download File CAD Drafter (.DXF)",
        data=generate_dxf(panjang, lebar),
        file_name=f"Deluxy_Plan_{panjang}x{lebar}.dxf",
        mime="application/dxf",
        use_container_width=True
    )

# Footer Copyright
st.markdown(f"""
    <div class="footer-text">
        DELUXY.Ai Engine &copy; 2026. Designed & Developed by <b>{NAMA_PENCIPTA}</b>. All rights reserved.
    </div>
""", unsafe_allow_html=True)
