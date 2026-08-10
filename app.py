import streamlit as st
import ezdxf
import io
import plotly.graph_objects as go

# Konfigurasi Halaman DELUXY.Ai
st.set_page_config(
    page_title="DELUXY.Ai - AI Architectural Engine", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Branding
st.title("🏛️ DELUXY.Ai - AI Architect & Real 3D Renderer")
st.caption("Generator Arsitektur AI: Denah 2D, Model 3D Furnitur & Scale Human, RAB, dan Visualization Realistis")
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
    
    btn_generate = st.button("🚀 Kalkulasi, Render & Generate", use_container_width=True)

# 1. Denah 2D Interaktif
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="black", width=3), fillcolor="lightgray")
    
    # Ruangan
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.5, y1=l*0.5, fillcolor="#FFE4C4", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.25], y=[l*0.25], text=["<b>Ruang Tamu & Sofa</b>"], mode="text"))

    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD700", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama (Kasur King)</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.7, y1=l, fillcolor="#ADD8E6", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.75], text=["<b>Kamar Anak & KM</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.5, y0=0, x1=p*0.7, y1=l*0.5, fillcolor="#D3D3D3", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.6], y=[l*0.25], text=["<b>Kitchen Set / Dapur</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.7, y0=0, x1=p, y1=l, fillcolor="#00FFFF", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.85], y=[l*0.5], text=["<b>Kolam Renang</b>"], mode="text"))

    fig.update_xaxes(title="Lebar (m)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang (m)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# 2. Model 3D Lengkap dengan Manusia & Elemen Interior
def generate_3d_house_with_furniture(p, l, h_lantai, show_roof):
    fig = go.Figure()

    # Dinding Transparan
    fig.add_trace(go.Mesh3d(
        x=[0, p, p, 0, 0, p, p, 0], y=[0, 0, l, l, 0, 0, l, l],
        z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
        color='lightgray', opacity=0.15, name="Dinding Luar"
    ))

    # --- ELEMENT INTERIOR ---
    # Tempat Tidur (Kasur) Kamar Utama
    fig.add_trace(go.Mesh3d(
        x=[p*0.05, p*0.25, p*0.25, p*0.05, p*0.05, p*0.25, p*0.25, p*0.05],
        y=[l*0.7, l*0.7, l*0.9, l*0.9, l*0.7, l*0.7, l*0.9, l*0.9],
        z=[0, 0, 0, 0, 0.6, 0.6, 0.6, 0.6],
        color='brown', opacity=0.9, name="Tempat Tidur (Bed)"
    ))

    # Dapur (Kitchen Counter/Meja Dapur)
    fig.add_trace(go.Mesh3d(
        x=[p*0.52, p*0.68, p*0.68, p*0.52, p*0.52, p*0.68, p*0.68, p*0.52],
        y=[l*0.05, l*0.05, l*0.2, l*0.2, l*0.05, l*0.05, l*0.2, l*0.2],
        z=[0, 0, 0, 0, 0.9, 0.9, 0.9, 0.9],
        color='darkgray', opacity=0.9, name="Dapur (Kitchen Cabinet)"
    ))

    # Sofa Ruang Tamu
    fig.add_trace(go.Mesh3d(
        x=[p*0.1, p*0.35, p*0.35, p*0.1, p*0.1, p*0.35, p*0.35, p*0.1],
        y=[l*0.1, l*0.1, l*0.25, l*0.25, l*0.1, l*0.1, l*0.25, l*0.25],
        z=[0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5],
        color='purple', opacity=0.8, name="Sofa Ruang Tamu"
    ))

    # Kolam Renang
    fig.add_trace(go.Mesh3d(
        x=[p*0.7, p, p, p*0.7, p*0.7, p, p, p*0.7],
        y=[0, 0, l, l, 0, 0, l, l],
        z=[-1, -1, -1, -1, 0, 0, 0, 0],
        color='deepskyblue', opacity=0.8, name="Kolam Renang"
    ))

    # --- SKALA MANUSIA (ORANG / HUMAN FIGURE 1.7m) ---
    # Diwakili dengan silinder/balok skala manusia di dekat kolam & ruang tamu
    fig.add_trace(go.Mesh3d(
        x=[p*0.65, p*0.68, p*0.68, p*0.65, p*0.65, p*0.68, p*0.68, p*0.65],
        y=[l*0.4, l*0.4, l*0.43, l*0.43, l*0.4, l*0.4, l*0.43, l*0.43],
        z=[0, 0, 0, 0, 1.7, 1.7, 1.7, 1.7],
        color='red', opacity=1.0, name="Manusia / Human Scale (1.7m)"
    ))

    if show_roof:
        fig.add_trace(go.Mesh3d(
            x=[0, p, p/2, 0, p, p/2], y=[0, 0, l/2, l, l, l/2],
            z=[h_lantai, h_lantai, h_lantai + 2, h_lantai, h_lantai, h_lantai + 2],
            color='firebrick', opacity=0.7, name="Atap"
        ))

    fig.update_layout(
        scene=dict(xaxis_title='P (m)', yaxis_title='L (m)', zaxis_title='T (m)', aspectmode='data'),
        margin=dict(r=10, l=10, b=10, t=10), height=450
    )
    return fig

# Engineering & RAB
def calculate_engineering_data(p, l, jml_lantai, bg_budget):
    luas_tanah = p * l
    luas_bangunan = luas_tanah * 0.6 * jml_lantai
    harga_per_m2 = 4500000 if jml_lantai == 1 else 5500000
    est_biaya_konstruksi = luas_bangunan * harga_per_m2
    return luas_tanah, luas_bangunan, est_biaya_konstruksi, int(luas_bangunan * 1.2), int(luas_bangunan * 70), int(luas_bangunan * 2.5)

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
            st.success("✅ Generasi 3D Furnitur, Skala Manusia & Render Visual Berhasil!")
            lt, lb, est_biaya, semen, bata, besi = calculate_engineering_data(panjang, lebar, lantai, budget)
            
            tab_real, tab1, tab2, tab3 = st.tabs([
                "📸 Visualisasi Realistis AI (Foto Nyata)", 
                "📐 Layout 2D & 3D (Ada Furnitur & Orang)", 
                "📊 RAB & Material Engineering", 
                "📄 Spesifikasi Ruangan"
            ])
            
            with tab_real:
                st.subheader("🖼️ Render Visual Realistis Bangunan (AI Engine)")
                st.caption("Berikut adalah prediksi visualisasi fisik asli rumah hasil interpretasi AI:")
                
                # Menggunakan AI Dynamic Image Rendering Service berdasarkan Prompt
                clean_prompt = prompt.replace(" ", "%20")
                img_eksterior = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20luxury%20house%20architecture,%20exterior,%20{clean_prompt},%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=600&seed=42"
                img_interior_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya.lower()}%20style,%20modern%20furniture,%20warm%20lighting?width=512&height=350&seed=12"
                img_interior_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20interior%20design,%20marble%20island,%20{gaya.lower()}%20style?width=512&height=350&seed=88"
                
                st.image(img_eksterior, caption="Tampilan Fisik Nyata Eksterior Rumah & Kolam Renang", use_container_width=True)
                
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.image(img_interior_kamar, caption="Visual Nyata Interior Kamar Utama", use_container_width=True)
                with col_img2:
                    st.image(img_interior_dapur, caption="Visual Nyata Interior Dapur (Kitchen)", use_container_width=True)

            with tab1:
                st.subheader("1. Denah Layout Ruangan 2D")
                st.plotly_chart(generate_2d_floorplan(panjang, lebar), use_container_width=True)
                
                st.subheader("2. Model 3D dengan Furnitur & Skala Manusia (Warna Merah)")
                st.caption("Atur sudut pandang 3D untuk melihat letak Kasur (Cokelat), Dapur (Abu-abu), Sofa (Ungu), dan Skala Orang (Merah).")
                st.plotly_chart(generate_3d_house_with_furniture(panjang, lebar, 3.5 * lantai, tampilkan_atap), use_container_width=True)
                
            with tab2:
                st.subheader("📊 Analisis Teknik & RAB")
                m1, m2, m3 = st.columns(3)
                m1.metric("Luas Tanah", f"{lt} m²")
                m2.metric("Luas Bangunan", f"{lb:.1f} m²")
                m3.metric("Estimasi Biaya", f"Rp {est_biaya:,.0f}")
                
                st.markdown("---")
                st.write("**Estimasi Kebutuhan Material Utama:**")
                st.write(f"- 🧱 **Batu Bata / Hebel:** ± {bata:,} Pcs")
                st.write(f"- 📦 **Semen (50kg):** ± {semen:,} Sak")
                st.write(f"- 🏗️ **Besi Beton (10/12mm):** ± {besi:,} Batang")

            with tab3:
                st.subheader("🏡 Rencana Tata Ruang Operasional")
                st.write("- 🛋️ **Ruang Tamu & Dapur:** Area Depan & Tengah")
                st.write("- 🛏️ **Kamar Utama:** Area Kiri Atas (Dilengkapi Kasur & Lampu)")
                st.write("- 🛏️ **Kamar Anak:** Area Tengah Atas")
                st.write("- 🏊 **Kolam Renang:** Area Samping Outdoor (Dilengkapi Skala Manusia)")

            st.markdown("---")
            st.download_button(
                label="⬇️ Unduh File CAD Native (.dxf)",
                data=generate_dxf_file(panjang, lebar),
                file_name=f"DELUXY_Layout_{panjang}x{lebar}.dxf",
                mime="application/dxf",
                use_container_width=True
            )
        else:
            st.warning("Silakan isi deskripsi konsep terlebih dahulu.")
