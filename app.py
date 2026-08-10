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
st.caption("Developed & Created by **Daffa Hendrawinata** | Platform AI Arsitektur & Engineering RAB")
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
    
    mode_3d = st.radio("Mode Tampilan 3D:", ["Rumah Jadi + Pintu & Jendela Fasad", "Interior & Furnitur Lengkap (Open Roof)"])
    
    btn_generate = st.button("🚀 Kalkulasi, Render & Generate", use_container_width=True)

# Helper Balok 3D
def create_box(x_min, x_max, y_min, y_max, z_min, z_max, color, opacity, name):
    x = [x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min]
    y = [y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max]
    z = [z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max]
    i = [7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]
    j = [3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6]
    k = [0, 7, 2, 3, 6, 7, 7, 5, 5, 5, 6, 2]
    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opacity, name=name)

# Model 3D dengan Pintu, Jendela, & Elemen Hidup
def generate_detailed_3d_house(p, l, h_lantai, mode):
    fig = go.Figure()

    # Rumput Halaman
    fig.add_trace(create_box(-2, p+2, -2, l+2, -0.2, 0.0, '#4CAF50', 1.0, "Rumput Taman"))
    
    # Fondasi/Teras
    fig.add_trace(create_box(0, p*0.7, 0, l, 0.0, 0.2, '#E0E0E0', 1.0, "Lantai & Teras"))

    if mode == "Rumah Jadi + Pintu & Jendela Fasad":
        # Dinding Utama
        fig.add_trace(create_box(0, p*0.7, 0, l, 0.2, h_lantai, '#FAF0E6', 1.0, "Dinding Utama"))

        # PINTU UTAMA (Kayu Cokelat Tua)
        fig.add_trace(create_box(p*0.1, p*0.25, -0.05, 0.21, 0.2, h_lantai*0.65, '#5C4033', 1.0, "Pintu Utama Kayu"))
        fig.add_trace(create_box(p*0.22, p*0.24, -0.08, -0.05, h_lantai*0.3, h_lantai*0.35, '#FFD700', 1.0, "Gagang Pintu"))

        # JENDELA KACA DEPAN (Biru Transparan + Bingkai Hitam)
        fig.add_trace(create_box(p*0.32, p*0.6, -0.05, 0.21, h_lantai*0.25, h_lantai*0.8, '#000000', 1.0, "Kusen Jendela"))
        fig.add_trace(create_box(p*0.33, p*0.59, -0.06, 0.2, h_lantai*0.27, h_lantai*0.78, '#87CEEB', 0.8, "Kaca Jendela Modern"))

        # JENDELA SAMPING
        fig.add_trace(create_box(-0.05, 0.21, l*0.3, l*0.6, h_lantai*0.3, h_lantai*0.75, '#87CEEB', 0.8, "Jendela Samping"))

        # ATAP MODERN
        x_roof = [0, p*0.7, p*0.7, 0, (p*0.7)/2]
        y_roof = [0, 0, l, l, l/2]
        z_roof = [h_lantai, h_lantai, h_lantai, h_lantai, h_lantai + 2.2]
        fig.add_trace(go.Mesh3d(x=x_roof, y=y_roof, z=z_roof, i=[0,1,2,3], j=[1,2,3,0], k=[4,4,4,4], color='#8B0000', opacity=1.0, name="Atap Limas"))

    else:
        # Mode Interior Furnitur
        fig.add_trace(create_box(0, p*0.7, 0, 0.15, 0.2, h_lantai*0.3, '#A9A9A9', 0.5, "Dinding"))
        fig.add_trace(create_box(p*0.05, p*0.25, l*0.65, l*0.9, 0.2, 0.6, '#8B4513', 1.0, "Ranjang Kasur"))
        fig.add_trace(create_box(p*0.06, p*0.24, l*0.66, l*0.89, 0.6, 0.8, '#FFFFFF', 1.0, "Kasur Busa"))
        fig.add_trace(create_box(p*0.4, p*0.65, l*0.05, l*0.2, 0.2, 1.0, '#2F4F4F', 1.0, "Kitchen Set"))
        fig.add_trace(create_box(p*0.08, p*0.3, l*0.1, l*0.22, 0.2, 0.6, '#4B0082', 1.0, "Sofa"))

    # Kolam Renang (Air & Keramik)
    fig.add_trace(create_box(p*0.73, p*0.97, l*0.1, l*0.9, -1.0, 0.0, '#00FFFF', 0.85, "Air Kolam"))
    fig.add_trace(create_box(p*0.71, p*0.99, l*0.08, l*0.92, -1.05, -1.0, '#D3D3D3', 1.0, "Keramik Kolam"))

    # Skala Manusia
    fig.add_trace(create_box(p*0.75, p*0.77, l*0.02, l*0.05, 0.0, 1.7, '#FF0000', 1.0, "Orang (1.7m)"))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Panjang (m)'),
            yaxis=dict(title='Lebar (m)'),
            zaxis=dict(title='Tinggi (m)'),
            aspectmode='data'
        ),
        margin=dict(r=10, l=10, b=10, t=10), height=500
    )
    return fig

# Denah 2D
def generate_2d_floorplan(p, l):
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=p, y1=l, line=dict(color="black", width=3), fillcolor="#F5F5F5")
    fig.add_shape(type="rect", x0=0, y0=0, x1=p*0.5, y1=l*0.5, fillcolor="#FFE4C4", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.25], y=[l*0.25], text=["<b>Ruang Tamu & Sofa</b>"], mode="text"))
    fig.add_shape(type="rect", x0=0, y0=l*0.5, x1=p*0.4, y1=l, fillcolor="#FFD700", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.2], y=[l*0.75], text=["<b>Kamar Utama</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.4, y0=l*0.5, x1=p*0.7, y1=l, fillcolor="#ADD8E6", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.55], y=[l*0.75], text=["<b>Kamar Anak & KM</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.5, y0=0, x1=p*0.7, y1=l*0.5, fillcolor="#D3D3D3", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.6], y=[l*0.25], text=["<b>Kitchen Set Dapur</b>"], mode="text"))
    fig.add_shape(type="rect", x0=p*0.7, y0=0, x1=p, y1=l, fillcolor="#00FFFF", line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=[p*0.85], y=[l*0.5], text=["<b>Kolam Renang</b>"], mode="text"))
    fig.update_xaxes(title="Lebar (m)", range=[-1, p+1])
    fig.update_yaxes(title="Panjang (m)", range=[-1, l+1], scaleanchor="x", scaleratio=1)
    fig.update_layout(showlegend=False, height=400, margin=dict(l=10, r=10, t=30, b=10))
    return fig

# Engineering RAB
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
            st.success("✅ Generasi Desain Arsitektur Realistis & Perhitungan RAB Berhasil!")
            lt, lb, est_biaya, semen, bata, besi = calculate_engineering_data(panjang, lebar, lantai, budget)
            
            tab_real, tab1, tab2, tab3 = st.tabs([
                "📸 Visualisasi Realistis AI (Foto Nyata)", 
                "🏠 Model 3D CAD & Fasad Pintu/Jendela", 
                "📊 RAB & Material Engineering", 
                "📄 Layout 2D & Spesifikasi"
            ])
            
            with tab_real:
                st.subheader("🖼️ Render Visual Realistis Bangunan Asli")
                st.caption("Prediksi wujud asli rumah hasil pengolahan AI berdasarkan spesifikasi input:")
                clean_prompt = prompt.replace(" ", "%20")
                img_eksterior = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20luxury%20house%20architecture,%20exterior,%20{clean_prompt},%20wooden%20door,%20large%20glass%20windows,%20swimming%20pool,%20archdaily%20style,%208k%20resolution?width=1024&height=600&seed=42"
                img_interior_kamar = f"https://image.pollinations.ai/prompt/photorealistic%20luxury%20master%20bedroom%20interior%20design,%20{gaya.lower()}%20style,%20bed,%20large%20window?width=512&height=350&seed=12"
                img_interior_dapur = f"https://image.pollinations.ai/prompt/photorealistic%20modern%20kitchen%20interior%20design,%20marble%20island,%20{gaya.lower()}%20style?width=512&height=350&seed=88"
                
                st.image(img_eksterior, caption="Visual Asli Eksterior Rumah, Pintu, Jendela & Kolam Renang", use_container_width=True)
                col_img1, col_img2 = st.columns(2)
                with col_img1:
                    st.image(img_interior_kamar, caption="Visual Asli Interior Kamar Utama", use_container_width=True)
                with col_img2:
                    st.image(img_interior_dapur, caption="Visual Asli Interior Dapur Modern", use_container_width=True)

            with tab1:
                st.subheader(f"Model 3D CAD: {mode_3d}")
                st.caption("Sudah dilengkapi Pintu Kayu (Cokelat Tua), Gagang Emas, Jendela Kaca (Biru Transparan), dan Kolam Renang.")
                st.plotly_chart(generate_detailed_3d_house(panjang, lebar, 3.5 * lantai, mode_3d), use_container_width=True)

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
                st.subheader("🏡 Denah Layout Ruangan 2D")
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

# Credit Creator
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "© 2026 DELUXY.Ai Engine. Developed & Created by <b>Daffa Hendrawinata</b>. All Rights Reserved."
    "</div>", 
    unsafe_allow_html=True
)
