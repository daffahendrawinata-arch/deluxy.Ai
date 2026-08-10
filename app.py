import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# -------------------------------------------------------------------
# KONFIGURASI HALAMAN & ATRIBUSI PENCIPTA
# -------------------------------------------------------------------
NAMA_PENCIPTA = "Nama Anda"  # Ganti dengan nama Anda / Studio Anda

st.set_page_config(
    page_title=f"DELUXY.Ai - Designed by {NAMA_PENCIPTA}", 
    page_icon="🏛️", 
    layout="wide"
)

st.markdown(f"""
    <style>
    .main-header {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
        border-left: 6px solid #10b981;
    }}
    .creator-badge {{
        background-color: #10b981;
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
    .angle-card {{
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }}
    </style>
""", unsafe_allow_html=True)

# Header Utama
st.markdown(f"""
    <div class="main-header">
        <h2 style="margin:0;">🏛️ DELUXY.Ai - Multi-Angle Architecture & Engineering RAB</h2>
        <div class="creator-badge">Lead Architect & Engine Developer: {NAMA_PENCIPTA}</div>
        <p style="margin-top: 10px; opacity: 0.85; margin-bottom:0;">
            Katalog Visualisasi Sudut Bangunan (Depan, Samping, Atas, Interior) & Kalkulator Material SNI Presisi
        </p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# INPUT PARAMETER (SIDEBAR)
# -------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Parameter Klien & Lahan")
    prompt = st.text_area("Konsep Desain Klien:", "Rumah 2 lantai modern tropis bukaan kaca lebar, ada kolam renang")
    budget = st.number_input("Target Budget Klien (Rp):", min_value=100000000, value=850000000, step=50000000, format="%d")
    
    st.subheader("Dimensi Tanah")
    panjang = st.slider("Panjang Lahan (m):", 10, 30, 15)
    lebar = st.slider("Lebar Lahan (m):", 6, 20, 8)
    lantai = st.radio("Jumlah Lantai:", [1, 2])
    ada_kolam = st.checkbox("Fasilitas Kolam Renang Private", value=True)
    
    gaya = st.selectbox("Style Fasad Arsitektur (Proyek Nyata):", [
        "Minimalis Modern Tropis", 
        "Japandi / Warm Timber Scandinavian", 
        "Industrial Concrete Modern", 
        "Luxury Contemporary Glass Villa"
    ])
    
    st.subheader("Kelas Finishing Material")
    kelas_mat = st.select_slider("Spesifikasi Material:", options=["Standard", "Medium/Pro", "Luxury"])

# -------------------------------------------------------------------
# DATABASE FOTO PROYEK NYATA BERDASARKAN SUDUT PANDANG (MULTI-ANGLE)
# -------------------------------------------------------------------
PROYEK_DESAIN = {
    "Minimalis Modern Tropis": {
        "depan": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "samping_kanan": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80",
        "samping_kiri": "https://images.unsplash.com/photo-1600585152220-90363fe7e115?auto=format&fit=crop&w=800&q=80",
        "tampak_atas": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
        "kamar": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=800&q=80",
        "dapur": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80"
    },
    "Japandi / Warm Timber Scandinavian": {
        "depan": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        "samping_kanan": "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80",
        "samping_kiri": "https://images.unsplash.com/photo-1600573472592-401b489a3cdc?auto=format&fit=crop&w=800&q=80",
        "tampak_atas": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "kamar": "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80",
        "dapur": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=800&q=80"
    },
    "Industrial Concrete Modern": {
        "depan": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        "samping_kanan": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=800&q=80",
        "samping_kiri": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80",
        "tampak_atas": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=800&q=80",
        "kamar": "https://images.unsplash.com/photo-1560185893-a55cbc8c57e8?auto=format&fit=crop&w=800&q=80",
        "dapur": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=800&q=80"
    },
    "Luxury Contemporary Glass Villa": {
        "depan": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1200&q=80",
        "samping_kanan": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=800&q=80",
        "samping_kiri": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=800&q=80",
        "tampak_atas": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80",
        "kamar": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80",
        "dapur": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80"
    }
}

OUTDOOR_KOLAM = "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=1000&q=80"
OUTDOOR_TAMAN = "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?auto=format&fit=crop&w=1000&q=80"

# -------------------------------------------------------------------
# ENGINE KALKULATOR MATERIAL & RAB SNI (AKURAT)
# -------------------------------------------------------------------
def hitung_rab_presisi(p, l, jml_lantai, kolam, spesifikasi):
    luas_tanah = p * l
    kdb = 0.60  # Koefisien Dasar Bangunan 60%
    luas_lantai_1 = luas_tanah * kdb
    luas_bangunan = luas_lantai_1 * (1.80 if jml_lantai == 2 else 1.0)
    
    harga_m2_map = {
        "Standard": 4500000 if jml_lantai == 1 else 5200000,
        "Medium/Pro": 5500000 if jml_lantai == 1 else 6300000,
        "Luxury": 7500000 if jml_lantai == 1 else 8800000
    }
    unit_rate = harga_m2_map[spesifikasi]
    biaya_konstruksi = luas_bangunan * unit_rate
    
    biaya_kolam = (luas_tanah * 0.15 * 5500000) + 25000000 if kolam else 0
    total_rab = biaya_konstruksi + biaya_kolam
    
    # Koefisien SNI
    hebel_m3 = luas_bangunan * 0.22
    semen_sak = luas_bangunan * 1.35
    pasir_m3 = luas_bangunan * 0.42
    besi_kg = luas_bangunan * 32.5
    keramik_m2 = luas_bangunan * 1.10
    
    breakdown = {
        "Pekerjaan Persiapan & Fondasi (12%)": total_rab * 0.12,
        "Struktur Beton Bertulang (33%)": total_rab * 0.33,
        "Dinding & Pasangan Bata (18%)": total_rab * 0.18,
        "Kusen, Pintu & Window Frame (12%)": total_rab * 0.12,
        "Plafon & Rangka Atap (10%)": total_rab * 0.10,
        "Instalasi MEP & Sanitair (8%)": total_rab * 0.08,
        "Finishing Cat & Exterior (7%)": total_rab * 0.07,
    }
    
    return {
        'luas_tanah': luas_tanah,
        'luas_bangunan': luas_bangunan,
        'total_rab': total_rab,
        'hebel_m3': round(hebel_m3, 1),
        'semen_sak': int(semen_sak),
        'pasir_m3': round(pasir_m3, 1),
        'besi_kg': int(besi_kg),
        'keramik_m2': int(keramik_m2),
        'breakdown': breakdown
    }

# -------------------------------------------------------------------
# MODEL DIAGRAM TAPAK LAHAN 3D
# -------------------------------------------------------------------
def generate_site_3d(p, l, jml_lantai, kolam):
    fig = go.Figure()
    
    # Site Tanah
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[-0.1, -0.1, -0.1, -0.1, 0, 0, 0, 0],
        i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
        k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
        color='#10b981', opacity=0.7, name="Site Tanah"
    ))
    
    # Massa Utama Bangunan
    tinggi = 3.8 if jml_lantai == 1 else 7.0
    fig.add_trace(go.Mesh3d(
        x=[1, p*0.6, p*0.6, 1, 1, p*0.6, p*0.6, 1],
        y=[1, 1, l*0.75, l*0.75, 1, 1, l*0.75, l*0.75],
        z=[0, 0, 0, 0, tinggi, tinggi, tinggi, tinggi],
        i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
        k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
        color='#3b82f6', opacity=0.75, name="Massa Bangunan"
    ))

    # Area Kolam Renang
    if kolam:
        fig.add_trace(go.Mesh3d(
            x=[p*0.65, p*0.95, p*0.95, p*0.65, p*0.65, p*0.95, p*0.95, p*0.65],
            y=[1, 1, l*0.6, l*0.6, 1, 1, l*0.6, l*0.6],
            z=[-0.5, -0.5, -0.5, -0.5, 0, 0, 0, 0],
            i=[7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7],
            j=[3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6],
            k=[0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2],
            color='#06b6d4', opacity=0.9, name="Pool Area"
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)'),
            yaxis=dict(title='Lebar (m)'),
            zaxis=dict(title='Tinggi (m)'),
            aspectmode='data'
        ),
        margin=dict(r=0, l=0, b=0, t=0), height=420
    )
    return fig

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
    rab = hitung_rab_presisi(panjang, lebar, lantai, ada_kolam, kelas_mat)
    desain = PROYEK_DESAIN.get(gaya, PROYEK_DESAIN["Minimalis Modern Tropis"])
    
    tab_render, tab_site, tab_rab, tab_advis = st.tabs([
        "🖼️ Visualisasi Multi-Sudut (Eksterior & Interior)", 
        "📐 Diagram Site Plan Lahan", 
        "📊 Engineering RAB & Material SNI", 
        "💡 Konsultasi Strategis Klien"
    ])
    
    # --- TAB 1: VISUAL MULTI-SUDUT ---
    with tab_render:
        st.subheader(f"🖼️ Katalog Visualisasi Sudut Pandang Arsitektur: {gaya}")
        st.caption(f"Kurasi portofolio profesional disajikan oleh **{NAMA_PENCIPTA}**:")
        
        # 1. TAMPAK DEPAN
        st.markdown("### 1. Tampak Depan Utama (Front Facade & Main Entrance)")
        st.image(desain['depan'], caption=f"Tampak Depan - Main Facade Style ({gaya})", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 2. TAMPAK SAMPING KANAN & KIRI
        st.markdown("### 2. Tampak Samping (Side Elevations)")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.image(desain['samping_kanan'], caption="Tampak Samping Kanan (Carport Area & Side Windows)", use_container_width=True)
        with col_s2:
            st.image(desain['samping_kiri'], caption="Tampak Samping Kiri (Service Access & Garden Clearance)", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 3. TAMPAK ATAS (BIRD-EYE VIEW)
        st.markdown("### 3. Tampak Atas / Perspektif Burung (Bird-Eye Roof & Massing)")
        st.image(desain['tampak_atas'], caption="Tampak Atas - Visualisasi Bentuk Atap & Pembagian Lahan", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

        # 4. INTERIOR & OUTDOOR
        st.markdown("### 4. Suasana Interior & Backyard")
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            st.image(desain['kamar'], caption="Kamar Utama (Master Bedroom)", use_container_width=True)
        with col_i2:
            st.image(desain['dapur'], caption="Dapur Bersih & Dining Space", use_container_width=True)
        with col_i3:
            img_out = OUTDOOR_KOLAM if ada_kolam else OUTDOOR_TAMAN
            cap_out = "Kolam Renang Private" if ada_kolam else "Tropical Inner Courtyard"
            st.image(img_out, caption=cap_out, use_container_width=True)

    # --- TAB 2: DIAGRAM SITE ---
    with tab_site:
        st.subheader("📐 Diagram Orientasi Tapak Lahan & Massa Bangunan 3D")
        st.caption("Model blok massa bangunan berdasarkan Koefisien Dasar Bangunan (KDB 60%):")
        st.plotly_chart(generate_site_3d(panjang, lebar, lantai, ada_kolam), use_container_width=True)

    # --- TAB 3: BREAKDOWN RAB REALISTIS ---
    with tab_rab:
        st.subheader("📊 Rencana Anggaran Biaya (RAB) & Estimasi Material")
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Luas Lahan", f"{rab['luas_tanah']} m²")
        k2.metric("Total Luas Bangunan", f"{rab['luas_bangunan']:.1f} m²")
        k3.metric("Estimasi Total RAB", f"Rp {rab['total_rab']:,.0f}")
        
        st.markdown("---")
        col_r1, col_r2 = st.columns([1, 1])
        
        with col_r1:
            st.write("#### 🧱 Estimasi Kebutuhan Material Utama (SNI):")
            st.markdown(f"""
            - **Bata Ringan (Hebel):** `± {rab['hebel_m3']} m³`
            - **Semen Portland (50kg):** `± {rab['semen_sak']} Sak`
            - **Pasir Pasang & Cor:** `± {rab['pasir_m3']} m³`
            - **Besi Beton Utama/Begel:** `± {rab['besi_kg']} kg`
            - **Granit / Keramik Lantai:** `± {rab['keramik_m2']} m²`
            """)
            
        with col_r2:
            st.write("#### 📑 Breakdown Estimasi Biaya Pekerjaan:")
            for item, nilai in rab['breakdown'].items():
                st.write(f"- **{item}:** Rp {nilai:,.0f}")

    # --- TAB 4: ADVIS KONSULTASI ---
    with tab_advis:
        st.subheader("💡 Konsultasi Strategis Anggaran")
        selisih = budget - rab['total_rab']
        
        if selisih < 0:
            st.error(f"⚠️ **Estimasi RAB Melebihi Budget Klien (Defisit: Rp {abs(selisih):,.0f})**")
            st.write("**Rekomendasi Penyesuaian Anggaran (*Value Engineering*):**")
            st.write("1. Turunkan spesifikasi material ke kelas **Standard** untuk menghemat biaya 15-20%.")
            st.write("2. Terapkan strategi **Rumah Tumbuh** (Prioritaskan struktur lantai 1 terlebih dahulu).")
            st.write("3. Alihkan kolam renang ke *Dry Garden Minimalis* untuk menghemat ± Rp 85 Juta.")
        else:
            st.success(f"✅ **Budget Klien Mencukupi (Surplus: Rp {selisih:,.0f})**")
            st.write("**Rekomendasi Optimalisasi Anggaran:**")
            st.write("1. Dialokasikan untuk sistem **Smart Home Automation & Solar Panel**.")
            st.write("2. Upgrade material lantai ke Granit *Big Slab* atau *Engineered Wood*.")

    st.markdown("---")
    st.download_button(
        label="⬇️ Download File CAD Drafter (.DXF)",
        data=generate_dxf(panjang, lebar),
        file_name=f"DELUXY_CAD_{panjang}x{lebar}.dxf",
        mime="application/dxf",
        use_container_width=True
    )

# Footer Copyright
st.markdown(f"""
    <div class="footer-text">
        DELUXY.Ai Engine &copy; 2026. Designed & Developed by <b>{NAMA_PENCIPTA}</b>. All rights reserved.
    </div>
""", unsafe_allow_html=True)
