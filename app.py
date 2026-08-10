import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# Konfigurasi Halaman DELUXY.Ai
st.set_page_config(
    page_title="DELUXY.Ai - Professional CAD & Engineering AI", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Branding
st.title("🏛️ DELUXY.Ai - Architectural & Engineering AI")
st.caption("Platform AI Generator Desain Rumah 3D Lengkap & Perhitungan Engineering RAB")
st.markdown("---")

# Layout 2 Kolom
col_input, col_output = st.columns([1, 2])

with col_input:
    st.subheader("⚙️ Parameter & Spesifikasi Input")
    prompt = st.text_area(
        "Deskripsi Konsep Rumah:", 
        placeholder="Contoh: Rumah minimalis budget 500jt ada kolam renang kecil",
        height=100
    )
    
    budget = st.number_input("Estimasi Budget (Rp):", min_value=100000000, value=500000000, step=50000000)
    gaya = st.selectbox("Gaya Arsitektur:", ["Minimalis Modern", "Mewah Kontemporer", "Klasik Modern", "Industrial"])
    panjang = st.slider("Panjang Lahan (m):", 10, 30, 15)
    lebar = st.slider("Lebar Lahan (m):", 6, 20, 10)
    lantai = st.radio("Jumlah Lantai:", [1, 2])
    
    btn_generate = st.button("🚀 Kalkulasi & Generate Desain 3D", use_container_width=True)

# Fungsi Pembuat Visualisasi 3D Komprehensif (Plotly Engine)
def generate_3d_house(p, l, h_lantai, gaya_arch):
    fig = go.Figure()

    # 1. Fondasi / Lantai Dasar
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[-0.2, -0.2, -0.2, -0.2, 0, 0, 0, 0],
        color='gray', opacity=0.8, name="Lantai & Fondasi"
    ))

    # 2. Dinding Utam
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
        color='whitesmoke', opacity=0.5, name="Dinding Utama"
    ))

    # 3. Kaca & Jendela Depan
    fig.add_trace(go.Mesh3d(
        x=[p*0.2, p*0.5, p*0.5, p*0.2, p*0.2, p*0.5, p*0.5, p*0.2],
        y=[0, 0, 0, 0, 0, 0, 0, 0],
        z=[0.5, 0.5, h_lantai*0.8, h_lantai*0.8, 0.5, 0.5, h_lantai*0.8, h_lantai*0.8],
        color='cyan', opacity=0.8, name="Fasad Kaca / Pintu Utama"
    ))

    # 4. Atap
    fig.add_trace(go.Mesh3d(
        x=[0, p, p/2, 0, p, p/2],
        y=[0, 0, l/2, l, l, l/2],
        z=[h_lantai, h_lantai, h_lantai + 2.5, h_lantai, h_lantai, h_lantai + 2.5],
        color='firebrick', opacity=0.9, name="Atap Bangunan"
    ))

    # 5. Kolam Renang (Jika Ada di Prompt)
    if "kolam" in prompt.lower():
        p_k, l_k = p * 0.3, l * 0.4
        fig.add_trace(go.Mesh3d(
            x=[p*0.6, p*0.6+p_k, p*0.6+p_k, p*0.6, p*0.6, p*0.6+p_k, p*0.6+p_k, p*0.6],
            y=[l*0.5, l*0.5, l*0.5+l_k, l*0.5+l_k, l*0.5, l*0.5, l*0.5+l_k, l*0.5+l_k],
            z=[-1.2, -1.2, -1.2, -1.2, 0, 0, 0, 0],
            color='deepskyblue', opacity=0.8, name="Kolam Renang"
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Panjang (m)',
            yaxis_title='Lebar (m)',
            zaxis_title='Tinggi (m)',
            aspectmode='data'
        ),
        margin=dict(r=10, l=10, b=10, t=10),
        height=500
    )
    return fig

# Fungsi Perhitungan Engineering (RAB & Material)
def calculate_engineering_data(p, l, jml_lantai, bg_budget):
    luas_tanah = p * l
    luas_bangunan = luas_tanah * 0.6 * jml_lantai  # KDB ~60%
    
    # Biaya rata-rata per m2 bangunan
    harga_per_m2 = 4500000 if jml_lantai == 1 else 5500000
    est_biaya_konstruksi = luas_bangunan * harga_per_m2
    
    # Estimasi Material
    semen_bag = int(luas_bangunan * 1.2)
    bata_m2 = int(luas_bangunan * 70)
    besi_beton_batang = int(luas_bangunan * 2.5)
    
    return luas_tanah, luas_bangunan, est_biaya_konstruksi, semen_bag, bata_m2, besi_beton_batang

# Fungsi Ekspor CAD Native (.dxf)
def generate_dxf_file(p, l):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0,0), (p,0), (p,l), (0,l), (0,0)], dxfattribs={"layer": "DINDING_LUAR"})
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

with col_output:
    if btn_generate:
        if prompt:
            st.success("✅ Generasi Desain & Kalkulasi Teknik Berhasil Dilakukan!")
            
            # Hitung Perhitungan Engineering
            lt, lb, est_biaya, semen, bata, besi = calculate_engineering_data(panjang, lebar, lantai, budget)
            
            # Tab Navigasi Visual & Data Teknik
            tab1, tab2, tab3 = st.tabs(["🏛️ Model 3D Arsitektur", "📊 Perhitungan Engineering & RAB", "📄 Spesifikasi Ruangan"])
            
            with tab1:
                st.write("**Visualisasi Struktur Rumah 3D (Putar, Zoom, & Tilt 360°):**")
                fig_3d = generate_3d_house(panjang, lebar, 3.5 * lantai, gaya)
                st.plotly_chart(fig_3d, use_container_width=True)
                
            with tab2:
                st.subheader("📊 Analisis Teknik & Rencana Anggaran Biaya (RAB)")
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Tanah", f"{lt} m²")
                m2.metric("Luas Bangunan", f"{lb:.1f} m²")
                m3.metric("Estimasi Biaya", f"Rp {est_biaya:,.0f}")
                
                if est_biaya > budget:
                    st.warning(f"⚠️ **Peringatan Budget:** Estimasi biaya konstruksi (Rp {est_biaya:,.0f}) melebihi budget target Anda (Rp {budget:,.0f}). Disarankan mengoptimalkan luas bangunan atau material.")
                else:
                    st.info(f"💡 **Status Budget:** Desain ini sesuai dengan target alokasi budget Anda.")
                
                st.markdown("---")
                st.write("**Estimasi Kebutuhan Material Utama:**")
                st.write(f"- 🧱 **Batu Bata / Hebel:** ± {bata:,} Pcs")
                st.write(f"- 📦 **Semen (50kg):** ± {semen:,} Sak")
                st.write(f"- 🏗️ **Besi Beton (10/12mm):** ± {besi:,} Batang")

            with tab3:
                st.subheader("🏡 Rencana Tata Ruang Operasional")
                st.write(f"**Distribusi Ruangan Otomatis ({lantai} Lantai):**")
                st.write("- 🛋️ **Ruang Tamu & Keluarga:** Integrated Open Space")
                st.write("- 🛏️ **Kamar Tidur Utama:** 1 Unit (Termasuk En-suite Bathroom)")
                st.write("- 🛏️ **Kamar Tidur Anak:** 1-2 Unit")
                st.write("- 🍳 **Dapur & Area Makan:** Modern Minimalis")
                if "kolam" in prompt.lower():
                    st.write("- 🏊 **Area Servis / Kolam Renang:** Plunge Pool Outdoor")

            st.markdown("---")
            # Unduh File CAD Native
            dxf_data = generate_dxf_file(panjang, lebar)
            st.download_button(
                label="⬇️ Unduh File CAD Native Kompleks (.dxf)",
                data=dxf_data,
                file_name=f"DELUXY_Engineering_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan isi deskripsi konsep terlebih dahulu.")
