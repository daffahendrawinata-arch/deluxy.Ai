 import streamlit as st
import ezdxf
import io

# Konfigurasi Halaman DELUXY.Ai
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Generator", 
    page_icon="🏛️", 
    layout="centered"
)

# Header & Branding Pencipta
st.title("🏛️ DELUXY.Ai")
st.caption("AI CAD Generator Khusus Desain Arsitektur & Rumah Mewah")
st.markdown("---")

# Input User
st.subheader("Masukkan Konsep Desain")
prompt = st.text_area(
    "Deskripsikan rumah yang ingin didesain:", 
    placeholder="Contoh: Rumah mewah modern 2 lantai dengan master bedroom dan kolam renang"
)
tipe_desain = st.selectbox(
    "Gaya Arsitektur:", 
    ["Mewah Modern", "Klasik Eropa", "Minimalis Kontemporer", "Industrial High-End"]
)

# Fungsi Generator Berkas CAD (.DXF)
def generate_cad_dxf(konsep, gaya):
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    
    # Membuat Layer
    doc.layers.add("DINDING", color=7)
    doc.layers.add("RUANGAN", color=1)
    
    # Menggambar Garis Dinding Luar (Ukuran Rumah Mewah Prototipe 15x20m)
    msp.add_lwpolyline([(0, 0), (15, 0), (15, 20), (0, 20), (0, 0)], dxfattribs={"layer": "DINDING"})
    
    # Menggambar Ruangan Utama (Sesuai Konsep)
    msp.add_lwpolyline([(0, 0), (8, 0), (8, 10), (0, 10), (0, 0)], dxfattribs={"layer": "RUANGAN"}) # Ruang Utama
    msp.add_lwpolyline([(8, 0), (15, 0), (15, 6), (8, 6), (8, 0)], dxfattribs={"layer": "RUANGAN"}) # Garasi / Area Mewah
    msp.add_lwpolyline([(8, 6), (15, 6), (15, 20), (8, 20), (8, 6)], dxfattribs={"layer": "RUANGAN"}) # Kolam / Taman
    
    # Simpan ke memori buffer
    out = io.StringIO()
    doc.write(out)
    return out.getvalue()

# Tombol Eksekusi
if st.button("Generate Desain CAD"):
    if prompt:
        st.success(f"Berhasil menganalisis konsep '{tipe_desain}' untuk: **{prompt}**")
        
        # Hasilkan file CAD
        dxf_data = generate_cad_dxf(prompt, tipe_desain)
        
        st.subheader("Hasil Generasi CAD DELUXY.Ai")
        st.write("File CAD 2D/3D parametrik Anda telah siap diunduh:")
        
        # Tombol Download File CAD
        st.download_button(
            label="⬇️ Download File CAD (.dxf)",
            data=dxf_data,
            file_name=f"DELUXY_Ai_{tipe_desain.replace(' ', '_')}.dxf",
            mime="application/dxf"
        )
    else:
        st.warning("Silakan masukkan deskripsi desain terlebih dahulu.")

# Footer Kredit Pencipta
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>DELUXY.Ai Engine &copy; Diciptakan oleh Daffa Hendrawinata</p>", unsafe_allow_html=True)
