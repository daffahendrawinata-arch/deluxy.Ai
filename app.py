import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN
# -------------------------------------------------------------------
st.set_page_config(
    page_title="DELUXY.Ai - Architectural & Engineering Engine", 
    page_icon="🏛️", 
    layout="wide"
)

st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        background-color: #f1f5f9;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h2 style="margin:0;">🏛️ DELUXY.Ai - Engine Arsitektur & RAB Presisi</h2>
        <p style="margin-top: 5px; opacity: 0.8;">Platform Pemodelan 3D Rapi, Kalkulasi RAB, & Advis Konsultasi Klien</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# SIDEBAR PARAMETER
# -------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Input Parameter Klien")
    prompt = st.text_area("Deskripsi / Konsep Klien:", "Rumah 2 lantai minimalis dengan pencahayaan alami dan kolam renang")
    budget = st.number_input("Target Budget (Rp):", min_value=100000000, value=650000000, step=50000000, format="%d")
    
    st.subheader("Ukuran Lahan")
    panjang = st.slider("Panjang Lahan (m):", 10, 30, 15)
    lebar = st.slider("Lebar Lahan (m):", 6, 20, 8)
    lantai = st.radio("Jumlah Lantai:", [1, 2])
    ada_kolam = st.checkbox("Sertakan Kolam Renang", value=True)
    
    gaya = st.selectbox("Gaya Arsitektur:", [
        "Minimalis Modern", 
        "Japandi / Skandinavia", 
        "Industrial Modern", 
        "Mewah Kontemporer"
    ])
    
    btn_generate = st.button("🚀 Render Model & Kalkulasi", use_container_width=True)

# -------------------------------------------------------------------
# HELPER MESH 3D RAPI (BALOK PRESISI)
# -------------------------------------------------------------------
def add_solid_box(fig, x_range, y_range, z_range, color, opacity=1.0, name=""):
    """Fungsi pembentuk balok 3D rapi tanpa garis silang melintang."""
    x0, x1 = x_range
    y0, y1 = y_range
    z0, z1 = z_range
    
    x = [x0, x1, x1, x0, x0, x1, x1, x0]
    y = [y0, y0, y1, y1, y0, y0, y1, y1]
    z = [z0, z0, z0, z0, z1, z1, z1, z1]
    
    # Indeks Segitiga untuk membentuk Kubus Rapi
    i = [7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]
    j = [3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6]
    k = [0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2]
    
    fig.add_trace(go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k,
        color=color, opacity=opacity,
        flatshading=True,
        lighting=dict(ambient=0.7, diffuse=0.8, specular=0.2),
        name=name, showlegend=False
    ))

# -------------------------------------------------------------------
# GENERATOR MODEL 3D BERSIH & RAPI
# -------------------------------------------------------------------
def render_clean_3d(p, l, jml_lantai, bg, gaya_pilihan, kolam):
    fig = go.Figure()
    
    # Skema Warna Berdasarkan Gaya
    if "Industrial" in gaya_pilihan:
        c_wall = '#4A4E69'; c_accent = '#9A8C98'; c_roof = '#22223B'
    elif "Japandi" in gaya_pilihan:
        c_wall = '#F4F1DE'; c_accent = '#E07A5F'; c_roof = '#3D405B'
    elif "Mewah" in gaya_pilihan:
        c_wall = '#E9ECEF'; c_accent = '#D4AF37'; c_roof = '#212529'
    else: # Minimalis
        c_wall = '#F8F9FA'; c_accent = '#6C584C'; c_roof = '#343A40'

    # 1. Base Tapak Lahan (Rumput & Carport)
    add_solid_box(fig, [-1, p+1], [-1, l+1], [-0.1, 0.0], '#38b000', name="Taman/Rumput")
    add_solid_box(fig, [0, 5], [0, 3.5], [0.0, 0.05], '#a0aab2', name="Carport")

    # 2. VARIATIVE BUILDING MASSING (BENTUK BEDA BERDASARKAN LANTAI & BUDGET)
    if jml_lantai == 1:
        # BENTUK 1: RUMAH COMPACT 1 LANTAI
        add_solid_box(fig, [1, p*0.65], [1, l*0.8], [0.0, 3.2], c_wall, name="Dinding L1")
        # Dinding Akses Fasad Depan
        add_solid_box(fig, [1, 3.5], [0.9, 1.0], [0.0, 3.2], c_accent, name="Aksen Fasad")
        # Atap Pelana Simetris
        fig.add_trace(go.Mesh3d(
            x=[0.8, p*0.67, p*0.67, 0.8, (1 + p*0.65)/2],
            y=[0.8, 0.8, l*0.82, l*0.82, (1 + l*0.8)/2],
            z=[3.2, 3.2, 3.2, 3.2, 4.8],
            i=[0, 1, 2, 3], j=[1, 2, 3, 0], k=[4, 4, 4, 4],
            color=c_roof, name="Atap"
        ))

    else: # 2 LANTAI
        if bg < 700000000:
            # BENTUK 2: MODULAR L-SHAPE 2 LANTAI (COMPACT MODERN)
            # Lantai 1
            add_solid_box(fig, [1, p*0.6], [1, l*0.5], [0.0, 3.2], c_wall, name="L1 Utama")
            add_solid_box(fig, [p*0.3, p*0.6], [l*0.5, l*0.85], [0.0, 3.2], c_wall, name="L1 Belakang")
            # Lantai 2 (Massa L-Shape Atas)
            add_solid_box(fig, [1, p*0.6], [1, l*0.5], [3.2, 6.2], c_accent, name="L2 Utama")
            # Canopy Balkon
            add_solid_box(fig, [0.8, p*0.3], [0.8, 1.1], [3.1, 3.25], '#212529', name="Kanopi Balkon")
            # Atap Datar Modern / Flat Roof Accent
            add_solid_box(fig, [0.8, p*0.62], [0.8, l*0.87], [6.2, 6.5], c_roof, name="Atap Dak Datar")
        else:
            # BENTUK 3: LUXURY STACKED CANTILEVER BOX (BUDGET TINGGI)
            # Lantai 1 (Base Dinding Kaca Terbuka)
            add_solid_box(fig, [1.5, p*0.7], [1.5, l*0.85], [0.0, 3.4], c_wall, name="L1 Glass Podium")
            # Lantai 2 (Box Melayang Lengkap dengan Frame Solid)
            add_solid_box(fig, [0.8, p*0.55], [1.0, l*0.65], [3.4, 6.8], c_accent, name="L2 Overhanging Cube")
            # Frame Aksen Hitam Tegas
            add_solid_box(fig, [0.7, p*0.57], [0.9, 1.05], [3.3, 6.9], '#111111', opacity=0.85, name="Frame Baja")
            # Balkon Kaca
            add_solid_box(fig, [0.8, p*0.55], [0.9, 1.0], [6.8, 7.6], '#48cae4', opacity=0.4, name="Railing Kaca")

    # 3. Kaca & Buka Jendela (Dipasang Rapi di Fasad Depan)
    add_solid_box(fig, [2.0, 4.0], [0.88, 0.98], [0.8, 2.5], '#90e0ef', opacity=0.6, name="Jendela Utama")
    add_solid_box(fig, [4.3, 5.2], [0.88, 0.98], [0.0, 2.2], '#3a5a40', name="Pintu Utam")

    # 4. Kolam Renang (Jika Dicentang)
    if kolam:
        add_solid_box(fig, [p*0.65, p*0.95], [1.0, l*0.7], [-0.4, 0.0], '#0077b6', name="Kolam Renang")
        add_solid_box(fig, [p*0.67, p*0.93], [1.2, l*0.68], [-0.3, -0.02], '#48cae4', opacity=0.8, name="Air Kolam")

    # Layout Kamera & Environment
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)', backgroundcolor="#f8f9fa"),
            yaxis=dict(title='Lebar (m)', backgroundcolor="#f8f9fa"),
            zaxis=dict(title='Tinggi (m)', backgroundcolor="#f8f9fa"),
            aspectmode='data',
            camera=dict(eye=dict(x=-1.5, y=-1.5, z=1.1))
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=520
    )
    return fig

# -------------------------------------------------------------------
# ENGINE KALKULASI ENGINEERING & RAB
# -------------------------------------------------------------------
def hitung_rab(p, l, jml_lantai, kolam):
    luas_tanah = p * l
    luas_lantai_1 = luas_tanah * 0.55
    luas_bangunan = luas_lantai_1 * (1.85 if jml_lantai == 2 else 1.0)
    
    biaya_m2 = 4800000 if jml_lantai == 1 else 5800000
    est_bangunan = luas_bangunan * biaya_m2
    biaya_kolam = 70000000 if kolam else 0
    total_rab = est_bangunan + biaya_kolam
    
    return {
        'luas_tanah': luas_tanah,
        'luas_bangunan': luas_bangunan,
        'total_rab': total_rab,
        'persiapan': total_rab * 0.05,
        'struktur': total_rab * 0.40,
        'dinding_finishing': total_rab * 0.30,
        'atap': total_rab * 0.13,
        'mep': total_rab * 0.12,
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
# MAIN TABS DISPLAY
# -------------------------------------------------------------------
if prompt:
    rab = hitung_rab(panjang, lebar, lantai, ada_kolam)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏠 Model 3D Geometri Presisi", 
        "🖼️ Visual Render Realistis", 
        "📊 RAB & Material Engineering", 
        "💡 Advis Konsultasi Klien"
    ])
    
    # TAB 1: 3D MODEL RAPI
    with tab1:
        st.subheader("🏠 Visualisasi 3D Geometri Rapi & Presisi")
        st.caption("Bentuk geometri disusun berdasarkan blok massa struktural yang rapi dan mudah dipahami:")
        st.plotly_chart(render_clean_3d(panjang, lebar, lantai, budget, gaya, ada_kolam), use_container_width=True)

    # TAB 2: RENDER DESAIN REALISTIS (FOTO)
    with tab2:
        st.subheader("🖼️ Referensi Render Fasad & Interior High-Definition")
        st.caption("Visual desain siap saji untuk dipresentasikan langsung kepada klien:")
        
        if budget >= 700000000:
            img_url = "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80"
            desc = "Fasad Luxury Modern 2 Lantai - Cantilever Box & Open Glass"
        elif lantai == 2:
            img_url = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
            desc = "Fasad Minimalis Modern 2 Lantai - Elegan & Clean Lines"
        else:
            img_url = "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80"
            desc = "Fasad Minimalis Compact 1 Lantai"
            
        st.image(img_url, caption=desc, use_container_width=True)
        
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.image("https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80", caption="Interior Kamar Utama", use_container_width=True)
        with c_i2:
            st.image("https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80", caption="Area Dapur & Dapur Bersih", use_container_width=True)

    # TAB 3: BREAKDOWN RAB
    with tab3:
        st.subheader("📊 Rencana Anggaran Biaya (RAB) Standard AHSP")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Luas Lahan", f"{rab['luas_tanah']} m²")
        k2.metric("Luas Bangunan Total", f"{rab['luas_bangunan']:.1f} m²")
        k3.metric("Estimasi Total Biaya", f"Rp {rab['total_rab']:,.0f}")
        
        st.markdown("---")
        st.write("#### 🧱 Estimasi Material Utama:")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.write(f"- **Bata Ringan / Hebel:** ± {rab['hebel_m3']} m³")
            st.write(f"- **Semen Sak (50kg):** ± {rab['semen_sak']} Sak")
        with col_m2:
            st.write(f"- **Besi Beton Ulir/Polos:** ± {rab['besi_batang']} Batang")

    # TAB 4: ADVIS KONSULTASI
    with tab4:
        st.subheader("💡 Saran Strategis untuk Klien")
        selisih = budget - rab['total_rab']
        
        if selisih < 0:
            st.error(f"⚠️ **Budget Klien Kurang sebesar: Rp {abs(selisih):,.0f}**")
            st.write("**Rekomendasi Solusi:**")
            st.write("1. **Sistem Rumah Tumbuh:** Tunda pembangunan lantai 2 atau finishing kolam renang.")
            st.write("2. **Penyesuaian Material:** Gunakan Rangka Atap Baja Ringan & Kusen Aluminium Standard.")
        else:
            st.success(f"✅ **Budget Klien Mencukupi (Sisa Anggaran: Rp {selisih:,.0f})**")
            st.write("**Rekomendasi Solusi:**")
            st.write("1. Dialokasikan untuk upgrade *interior built-in* (Kitchen Set) atau *Smart Home System*.")

    st.markdown("---")
    st.download_button(
        label="⬇️ Download File CAD Drafter (.DXF)",
        data=generate_dxf(panjang, lebar),
        file_name=f"Deluxy_Plan_{panjang}x{lebar}.dxf",
        mime="application/dxf",
        use_container_width=True
    )
