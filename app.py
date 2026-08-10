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
st.caption("Generator Arsitektur AI: Denah 2D, Model 3D Utuh Bangunan Jadi, RAB, dan Real Render")
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
    
    # Mode Tampilan 3D
    mode_3d = st.radio("Mode Tampilan 3D:", ["Rumah Jadi Utuh (Exterior Complete)", "Interior & Furnitur (Open Roof)"])
    
    btn_generate = st.button("🚀 Kalkulasi, Render & Generate", use_container_width=True)

# 1. Denah 2D Interaktif
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="black", width=3), fillcolor="#F5F5F5")
    
    # Ruangan
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.5, y1=l*0.5, fillcolor="#FFE4C4", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.25], y=[l*0.25], text=["<b>Ruang Tamu & Sofa</b>"], mode="text"))

    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD700", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.7, y1=l, fillcolor="#ADD8E6", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.75], text=["<b>Kamar Anak & KM</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.5, y0=0, x1=p*0.7, y1=l*0.5, fillcolor="#D3D3D3", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.6], y=[l*0.25], text=["<b>Dapur</b>"], mode="text"))

    fig.add_shape(type="rect", x0=p*0.7, y0=0, x1=p, y1=l, fillcolor="#00FFFF", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.85], y=[l*0.5], text=["<b>Kolam Renang</b>"], mode="text"))

    fig.update_xaxes(title="Lebar (m)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang (m)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# 2. Model 3D Bangunan Jadi & Interior
def generate_complete_3d_house(p, l, h_lantai, mode):
    fig = go.Figure()

    if mode == "Rumah Jadi Utuh (Exterior Complete)":
        # Pondasi / Decking Samping
        fig.add_trace(go.Mesh3d(
            x=[0, p, p, 0, 0, p, p, 0], y=[0, 0, l, l, 0, 0, l, l],
            z=[-0.2, -0.2, -0.2, -0.2, 0, 0, 0, 0],
            color='darkgrey', opacity=1.0, name="Pondasi & Teras"
        ))

        # Dinding Padat Fisik Rumah (Kerapatan Tinggi / Solid)
        fig.add_trace(go.Mesh3d(
            x=[0, p*0.7, p*0.7, 0, 0, p*0.7, p*0.7, 0],
            y=[0, 0, l, l, 0, 0, l, l],
            z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
            color='#F0EAE1', opacity=0.95, name="Dinding Bangunan Utama"
        ))

        # Fasad Kaca & Pintu Depan Modern
        fig.add_trace(go.Mesh3d(
            x=[p*0.1, p*0.4, p*0.4, p*0.1, p*0.1, p*0.4, p*0.4, p*0.1],
            y=[-0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05, -0.05],
            z=[0.2, 0.2, h_lantai*0.75, h_lantai*0.75, 0.2, 0.2, h_lantai*0.75, h_lantai*0.75],
            color='skyblue', opacity=0.85, name="Pintu Kaca & Jendela Fasad"
        ))

        # Atap Limas/Modern Jadi
        fig.add_trace(go.Mesh3d(
            x=[-0.5, p*0.75, p*0.75, -0.5, p*0.37, p*0.37],
            y=[-0.5, -0.5, l+0.5, l+0.5, l/2, l/2],
            z=[h_lantai, h_lantai, h_lantai, h_lantai, h_lantai + 2.2, h_lantai + 2.2],
            color='#8B0000', opacity=1.0, name="Atap Bangunan Jadi"
        ))

    else:
        # Mode Interior Transparan
        fig.add_trace(go.Mesh3d(
            x=[0, p*0.7, p*0.7, 0, 0, p*0.7, p*0.7, 0],
            y=[0, 0, l, l, 0, 0, l, l],
            z=[0, 0, 0, 0, h_lantai, h_lantai, h_lantai, h_lantai],
            color='lightgray', opacity=0.2, name="Dinding Outer"
        ))

        # Kasur Utama
        fig.add_trace(go.Mesh3d(
            x=[p*0.05, p*0.25, p*0.25, p*0.05, p*0.05, p*0.25, p*0.25, p*0.05],
            y=[l*0.7, l*0.7, l*0.9, l*0.9, l*0.7, l*0.7, l*0.9, l*0.9],
            z=[0, 0, 0, 0, 0.6, 0.6, 0.6, 0.6], color='saddlebrown', opacity=0.9, name="Tempat Tidur"
        ))

        # Dapur / Kitchen Island
        fig.add_trace(go.Mesh3d(
            x=[p*0.45, p*0.65, p*0.65, p*0.45, p*0.45, p*0.65, p*0.65, p*0.45],
            y=[l*0.05, l*0.05, l*0.2, l*0.2, l*0.05, l*0.05, l*0.2, l*0.2],
            z=[0, 0, 0, 0, 0.9, 0.9, 0.9, 0.9], color='gray', opacity=0.9, name="Kitchen Set"
        ))

        # Sofa
        fig.add_trace(go.Mesh3d(
            x=[p*0.1, p*0.35, p*0.35, p*0.1, p*0.1, p*0.35, p*0.35, p*0.1],
            y=[l*0.1, l*0.1, l*0.25, l*0.25, l*0.1, l*0.1, l*0.25, l*0.25],
            z=[0, 0, 0, 0, 0.5, 0.5, 0.5, 0.5], color='purple', opacity=0.8, name="Sofa"
        ))

    # Kolam Renang Area Outdoor (Selalu Ada di Kedua Mode)
    fig.add_trace(go.Mesh3d(
        x=[p*0.72, p*0.98, p*0.98, p*0.72, p*0.72, p*0.98, p*0.98, p*0.72],
        y=[l*0.1, l*0.1, l*0.9, l*0.9, l*0.1, l*0.1, l*0.9, l*0.9],
        z=[-1.2, -1.2, -1.2, -1.2, 0, 0, 0, 0],
        color='#00FFFF', opacity=0.85, name="Kolam Renang"
    ))

    # Skala Manusia (Human Scale 1.7m)
    fig.add_trace(go.Mesh3d(
        x=[p*0.75, p*0.78, p*0.78, p*0.75, p*0.75, p*0.78, p*0.78, p*0.75],
        y=[l*0.02, l*0.02, l*0.05, l*0.05, l*0.02, l*0.02, l*0.05, l*0.05],
        z=[0, 0, 0, 0, 1.7, 1.7, 1.7, 1.7],
        color='red', opacity=1.0, name="Manusia (1.7m)"
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Panjang (m)', 
            yaxis_title='Lebar (m)', 
            zaxis_title='Tinggi (m)', 
            aspectmode='data'
        ),
        margin=dict(r=10, l=10, b=10, t=10), height=500
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
            st.success("✅ Generasi Model 3D Bangunan Utuh Berhasil!")
            lt, lb, est_biaya, semen, bata, besi = calculate_engineering_data(panjang, lebar, lantai, budget)
            
            tab1, tab_real, tab2, tab3 = st.tabs([
                "🏠 Model 3D Utuh Bangunan Jadi", 
                "📸 Real Photorealistic Render", 
                "📊 RAB & Engineering Material", 
                "📄 Spesifikasi Ruangan"
            ])
            
            with tab1:
                st.subheader(f"Model 3D Interaktif: {mode_3d}")
                st.caption("Putar 360°, Zoom, dan geser untuk melihat bentuk nyata fisik rumah saat sudah jadi.")
                st.plotly_chart(generate_complete_3d_house(panjang, lebar, 3.5 * lantai, mode_3d), use_container_width=True)

            with tab_real:
                st.subheader("🖼️ Visual Render Asli Hasil AI")
                clean_prompt = prompt.replace(" ", "%20")
                img_eksterior = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20luxury%20house%20architecture,%20exterior,%20{clean_prompt},%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=600&seed=42"
                img_interior_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya.lower()}%20style,%20modern%20furniture?width=512&height=350&seed=12"
                img_interior_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20interior%20design,%20marble%20island,%20{gaya.lower()}%20style?width=512&height=350&seed=88"
                
                st.image(img_eksterior, caption="Visual Asli Eksterior Bangunan Jadi & Kolam Renang", use_container_width=True)
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.image(img_interior_kamar, caption="Kamar Utama Modern", use_container_width=True)
                with col_img2:
                    st.image(img_interior_dapur, caption="Dapur Modern", use_container_width=True)
                
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
                st.subheader("🏡 Denah 2D & Spesifikasi")
                st.plotly_chart(generate_2d_floorplan(panjang, lebar), use_container_width=True)

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
        
