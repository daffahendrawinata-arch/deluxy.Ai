import streamlit as st
import ezdxf
import io
import pydeck as pdk

# Konfigurasi Halaman DELUXY.Ai
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Generator 3D", 
    page_icon="🏛️", 
    layout="wide"
)

# Header & Branding
st.title("🏛️ DELUXY.Ai - 3D CAD Generator")
st.caption("AI CAD Generator Khusus Desain Arsitektur & Rumah Mewah 3D Interaktif")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Konsep Desain")
    prompt = st.text_area(
        "Deskripsikan rumah yang ingin didesain:", 
        placeholder="Contoh: Rumah mewah modern 2 lantai dengan master bedroom dan kolam renang",
        height=120
    )
    tipe_desain = st.selectbox(
        "Gaya Arsitektur:", 
        ["Mewah Modern", "Klasik Eropa", "Minimalis Kontemporer", "Industrial High-End"]
    )
    tinggi_bangunan = st.slider("Tinggi Elemen Bangunan (Meter):", 3, 12, 6)
    
    btn_generate = st.button("Generate Desain 3D", use_container_width=True)

# Fungsi Generator CAD (.dxf) & Data 3D
def generate_cad_and_3d(konsep, gaya, h):
    # 1. Buat File DXF CAD
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.layers.add("DINDING", color=7)
    doc.layers.add("RUANGAN", color=1)
    
    # Koordinat Denah Dasar (Meter)
    dinding_luar = [(0, 0), (15, 0), (15, 20), (0, 20), (0, 0)]
    r_utama = [(0, 0), (8, 0), (8, 10), (0, 10), (0, 0)]
    r_garasi = [(8, 0), (15, 0), (15, 6), (8, 6), (8, 0)]
    r_kolam = [(8, 6), (15, 6), (15, 20), (8, 20), (8, 6)]
    
    msp.add_lwpolyline(dinding_luar, dxfattribs={"layer": "DINDING"})
    msp.add_lwpolyline(r_utama, dxfattribs={"layer": "RUANGAN"})
    msp.add_lwpolyline(r_garasi, dxfattribs={"layer": "RUANGAN"})
    msp.add_lwpolyline(r_kolam, dxfattribs={"layer": "RUANGAN"})
    
    out = io.StringIO()
    doc.write(out)
    
    # 2. Data Poligon 3D (Extrusion) untuk PyDeck (Koordinat Lokal)
    # Konversi ke offset koordinat spasial
    data_3d = [
        {"name": "Bangunan Utama", "height": h, "color": [240, 240, 240, 220], 
         "polygon": [[-0.0001, -0.0001], [0.0007, -0.0001], [0.0007, 0.0009], [-0.0001, 0.0009]]},
        {"name": "Garasi High-End", "height": h * 0.6, "color": [100, 100, 100, 200], 
         "polygon": [[0.0007, -0.0001], [0.0013, -0.0001], [0.0013, 0.0005], [0.0007, 0.0005]]},
        {"name": "Area Kolam Luxury", "height": 0.5, "color": [0, 180, 230, 180], 
         "polygon": [[0.0007, 0.0005], [0.0013, 0.0005], [0.0013, 0.0018], [0.0007, 0.0018]]}
    ]
    
    return out.getvalue(), data_3d

with col2:
    if btn_generate:
        if prompt:
            st.success(f"Berhasil meng-generate model 3D untuk: **{prompt}**")
            dxf_data, data_3d = generate_cad_and_3d(prompt, tipe_desain, tinggi_bangunan)
            
            # View State Kamera 3D
            view_state = pdk.ViewState(
                latitude=0.0004,
                longitude=0.0006,
                zoom=17.5,
                pitch=55,   # Sudut kemiringan kamera 3D
                bearing=30  # Sudut putar kamera 3D
            )
            
            # Layer Ekstrusi 3D
            layer_3d = pdk.Layer(
                "PolygonLayer",
                data_3d,
                get_polygon="polygon",
                get_elevation="height",
                get_fill_color="color",
                extruded=True,
                wireframe=True,
                pickable=True
            )
            
            st.subheader("Model 3D Interaktif (Gunakan Mouse untuk Memutar & Zoom)")
            st.pydeck_chart(pdk.Deck(
                layers=[layer_3d],
                initial_view_state=view_state,
                tooltip={"text": "{name}"}
            ))
            
            # Tombol Download CAD
            st.download_button(
                label="⬇️ Unduh File CAD Native (.dxf)",
                data=dxf_data,
                file_name=f"DELUXY_Ai_3D_{tipe_desain.replace(' ', '_')}.dxf",
                mime="application/dxf"
            )
        else:
            st.warning("Silakan masukkan deskripsi konsep desain terlebih dahulu.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>DELUXY.Ai Engine 3D &copy; Diciptakan oleh Daffa Hendrawinata</p>", unsafe_allow_html=True)
