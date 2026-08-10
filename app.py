import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# Konfigurasi Halaman DELUXY.Ai
st.set_page_config(
    page_title="DELUXY.Ai - Architectural & Engineering AI", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Branding
st.title("🏛️ DELUXY.Ai - Architectural & Engineering AI")
st.caption("Platform AI Generator Desain Rumah 3D Lengkap & Perhitungan Engineering RAB")
st.markdown("---")

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
    tampilkan_atap = st.checkbox("Tampilkan Atap di 3D", value=False)
    
    btn_generate = st.button("🚀 Kalkulasi & Generate Desain 3D", use_container_width=True)

# 1. Denah 2D Interaktif dengan Label Ruangan
def generate_2d_floorplan(p, l):
    fig = go.Figure()

    # Dinding Luar
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="black", width=3), fillcolor="lightgray")
    
    # Ruang Tamu / Keluarga
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.5, y1=l*0.5, fillcolor="#FFE4C4", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.25], y=[l*0.25], text=["<b>Ruang Tamu & Utama</b>"], mode="text"))

    # Kamar Tidur Utama
    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD700", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama</b>"], mode="text"))

    # Kamar Anak / Mandi
    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.7, y1=l, fillcolor="#ADD8E6", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.75], text=["<b>Kamar Anak & KM</b>"], mode="text"))

    # Dapur & Makan
    fig.add_shape(type="rect", x0=p*0.5, y0=0, x1=p*0.7, y1=l*0.5, fillcolor="#D3D3D3", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.6], y=[l*0.25], text=["<b>Dapur</b>"], mode="text"))

    # Kolam Renang / Taman Belakang
    fig.add_shape(type="rect", x0=p*0.7, y0=0, x1=p, y1=l, fillcolor="#00FFFF", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.85], y=[l*0.5], text=["<b>Kolam Renang<br>& Taman</b>"], mode="text"))

    fig.update_xaxes(title="Lebar (m)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang (m)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=450, margin=dict(l=10, r=10, t=30, b=10), title="Denah 2D Layout Ruangan")
    return fig

# 2. Model 3D Transparan / Open Roof
def generate_3d_house_detailed(p, l, h_lantai, show_roof):
    fig = go.Figure()

    # Dinding Luar Transparan
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
        color='lightgray', opacity=0.2, name="Dinding Luar"
    ))

    # Sekat Kamar Utama
    fig.add_trace(go.Mesh3d(
        x=[p*0.4, p*0.4, p*0.4, p*0.4, 0, p*0.4, p*0.4, 0],
        y=[l*0.5, l*0.5, l, l, l*0.5, l*0.5, l, l],
        z=[0, 0, 0, 0, h_lantai*0.8, h_lantai*0.8, h_lantai*0.8, h_lantai*0.8],
        color='gold', opacity=0.6, name="Kamar Tidur Utama"
    ))

    # Sekat Kamar Anak
    fig.add_trace(go.Mesh3d(
        x=[p*0.4, p*0.7, p*0.7, p*0.4, p*0.4, p*0.7, p*0.7, p*0.4],
        y=[l*0.5, l*0.5, l, l, l*0.5, l*0.5, l, l],
        z=[0, 0, 0, 0, h_lantai*0.8, h_lantai*0.8, h_lantai*0.8, h_lantai*0.8],
        color='lightblue', opacity=0.6, name="Kamar Anak"
    ))

    # Kolam Renang
    fig.add_trace(go.Mesh3d(
        x=[p*0.7, p, p, p*0.7, p*0.7, p, p, p*0.7],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[-1, -1, -1, -1, 0, 0, 0, 0],
        color='cyan', opacity=0.8, name="Kolam Renang"
    ))

    # Atap (Opsional lewat Checkbox)
    if show_roof:
        fig.add_trace(go.Mesh3d(
            x=[0, p, p/2, 0, p, p/2],
            y=[0, 0, l/2, l, l, l/2],
            z=[h_lantai, h_lantai, h_lantai + 2, h_lantai, h_lantai, h_lantai + 2],
            color='firebrick', opacity=0.7, name="Atap"
        ))

    fig.update_layout(
        scene=dict(xaxis_title='P (m)', yaxis_title='L (m)', zaxis_title='T (m)', aspectmode='data'),
        margin=dict(r=10, l=10, b=10, t=10), height=450
    )
    return fig

# Engineering Data
def calculate_engineering_data(p, l, jml_lantai, bg_budget):
    luas_tanah = p * l
    luas_bangunan = luas_tanah * 0.6 * jml_lantai
    harga_per_m2 = 4500000 if jml_lantai == 1 else 5500000
    est_biaya_konstruksi = luas_bangunan * harga_per_m2
    semen_bag = int(luas_bangunan * 1.2)
    bata_m2 = int(luas_bangunan * 70)
    besi_beton_batang = int(luas_bangunan * 2.5)
    return luas_tanah, luas_bangunan, est_biaya_konstruksi, semen_bag, bata_m2, besi_beton_batang

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
            st.success("✅ Generasi Tata Ruang, Denah 2D & Model 3D Berhasil!")
            lt, lb, est_biaya, semen, bata, besi = calculate_engineering_data(panjang, lebar, lantai, budget)
            
            tab1, tab2, tab3 = st.tabs(["📐 Denah Layout & Visual 3D", "📊 Perhitungan Engineering RAB", "📄 Spesifikasi Ruangan"])
            
            with tab1:
                st.subheader("1. Denah Layout Ruangan 2D")
                fig_2d = generate_2d_floorplan(panjang, lebar)
                st.plotly_chart(fig_2d, use_container_width=True)
                
                st.subheader("2. Visualisasi Struktur 3D Open-Roof")
                fig_3d = generate_3d_house_detailed(panjang, lebar, 3.5 * lantai, tampilkan_atap)
                st.plotly_chart(fig_3d, use_container_width=True)
                
            with tab2:
                st.subheader("📊 Analisis Teknik & Rencana Anggaran Biaya (RAB)")
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Tanah", f"{lt} m²")
                m2.metric("Luas Bangunan", f"{lb:.1f} m²")
                m3.metric("Estimasi Biaya", f"Rp {est_biaya:,.0f}")
                
                if est_biaya > budget:
                    st.warning(f"⚠️ **Peringatan Budget:** Estimasi biaya konstruksi (Rp {est_biaya:,.0f}) melebihi budget target Anda (Rp {budget:,.0f}).")
                else:
                    st.info(f"💡 **Status Budget:** Desain ini sesuai dengan target alokasi budget Anda.")
                
                st.markdown("---")
                st.write("**Estimasi Kebutuhan Material Utama:**")
                st.write(f"- 🧱 **Batu Bata / Hebel:** ± {bata:,} Pcs")
                st.write(f"- 📦 **Semen (50kg):** ± {semen:,} Sak")
                st.write(f"- 🏗️ **Besi Beton (10/12mm):** ± {besi:,} Batang")

            with tab3:
                st.subheader("🏡 Rencana Tata Ruang Operasional")
                st.write("- 🛋️ **Ruang Tamu & Dapur:** Area Depan & Tengah")
                st.write("- 🛏️ **Kamar Utama:** Area Kiri Atas (Kuning)")
                st.write("- 🛏️ **Kamar Anak:** Area Tengah Atas (Biru Muda)")
                st.write("- 🏊 **Kolam Renang & Taman:** Area Samping/Belakang (Biru Laut)")

            st.markdown("---")
            dxf_data = generate_dxf_file(panjang, lebar)
            st.download_button(
                label="⬇️ Unduh File CAD Native (.dxf)",
                data=dxf_data,
                file_name=f"DELUXY_Layout_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan isi deskripsi konsep terlebih dahulu.")
