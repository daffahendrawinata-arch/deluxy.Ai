import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Generator",
    page_icon="⚙️",
    layout="wide"
)

# Style Header Custom
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚙️ DELUXY.Ai - Precision CAD Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform Desain Komponen Permesinan & Generator 3D CAD Berbasis Parametrik</div>', unsafe_allow_html=True)

# ================= SIDEBAR PARAMETER =================
st.sidebar.header("🎛️ Parameter Komponen")

komponen_type = st.sidebar.selectbox(
    "Pilih Tipe Komponen:",
    ["Poros Bertingkat (Shaft)", "Pelat Flensa Berlubang (Flange Plate)", "Siku Penopang (Bracket)"]
)

material = st.sidebar.selectbox(
    "Pilih Material:",
    ["Baja Carbon (ST37)", "Aluminium 6061", "Kuningan (Brass)", "Plastik ABS"]
)

# Massa jenis material dalam g/cm3
massa_jenis = {
    "Baja Carbon (ST37)": 7.85,
    "Aluminium 6061": 2.70,
    "Kuningan (Brass)": 8.40,
    "Plastik ABS": 1.05
}

st.sidebar.subheader("📐 Dimensi Utama (mm)")

# Inisialisasi variabel default
d1 = l1 = d2 = l2 = 0
d_outer = d_inner = tebal = jumlah_lubang = d_lubang = 0
p = l = t = tebal_b = 0

if komponen_type == "Poros Bertingkat (Shaft)":
    d1 = st.sidebar.slider("Diameter Bagian 1 (d1)", 10, 100, 30)
    l1 = st.sidebar.slider("Panjang Bagian 1 (l1)", 20, 200, 50)
    d2 = st.sidebar.slider("Diameter Bagian 2 (d2)", 10, 100, 45)
    l2 = st.sidebar.slider("Panjang Bagian 2 (l2)", 20, 200, 80)
    
    # Hitung Volume approx (cm3)
    v1 = np.pi * ((d1/10)/2)**2 * (l1/10)
    v2 = np.pi * ((d2/10)/2)**2 * (l2/10)
    total_volume = v1 + v2

elif komponen_type == "Pelat Flensa Berlubang (Flange Plate)":
    d_outer = st.sidebar.slider("Diameter Luar (OD)", 50, 300, 120)
    d_inner = st.sidebar.slider("Diameter Lubang Tengah (ID)", 10, 200, 40)
    tebal = st.sidebar.slider("Ketebalan (t)", 2, 50, 10)
    jumlah_lubang = st.sidebar.slider("Jumlah Lubang Baut", 3, 12, 4)
    d_lubang = st.sidebar.slider("Diameter Lubang Baut", 4, 20, 8)
    
    # Hitung Volume approx
    vol_base = np.pi * ((d_outer/10)/2)**2 * (tebal/10)
    vol_hole_center = np.pi * ((d_inner/10)/2)**2 * (tebal/10)
    vol_holes = jumlah_lubang * (np.pi * ((d_lubang/10)/2)**2 * (tebal/10))
    total_volume = max(0.1, vol_base - vol_hole_center - vol_holes)

else:  # Bracket
    p = st.sidebar.slider("Panjang Alas (P)", 30, 200, 80)
    l = st.sidebar.slider("Lebar (L)", 20, 150, 50)
    t = st.sidebar.slider("Tinggi (T)", 30, 200, 80)
    tebal_b = st.sidebar.slider("Tebal Dinding (t)", 3, 20, 6)
    
    total_volume = ((p/10 * l/10 * tebal_b/10) + ((t/10 - tebal_b/10) * l/10 * tebal_b/10))

# Berat & Estimasi Biaya
berat_gram = total_volume * massa_jenis[material]
harga_est = (berat_gram / 1000) * 150000 + 50000  # Perkiraan kasar biaya (IDR)

# ================= TAMPILAN UTAMA =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🧊 Pratinjau 3D CAD Interaktif")
    st.caption("Gunakan Klik Kiri Mouse untuk memutar objek 3D dan Scroll Wheel untuk Zoom.")

    # Generator HTML/ThreeJS Ringan untuk Render 3D
    def render_3d_viewer(k_type, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b):
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <style> body {{ margin: 0; overflow: hidden; background-color: #1a1a1a; }} canvas {{ width: 100%; height: 100%; }} </style>
        </head>
        <body>
            <script>
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x1a1a1a);

                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(100, 100, 150);

                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                // Pencahayaan
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                scene.add(ambientLight);
                const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
                dirLight.position.set(50, 100, 50);
                scene.add(dirLight);

                const grid = new THREE.GridHelper(200, 20, 0x444444, 0x222222);
                scene.add(grid);

                // Material Visual
                const material3D = new THREE.MeshStandardMaterial({{ 
                    color: 0x2196F3, 
                    metalness: 0.6, 
                    roughness: 0.3 
                }});

                const group = new THREE.Group();

                if ("{k_type}" === "Poros Bertingkat (Shaft)") {{
                    const geom1 = new THREE.CylinderGeometry({d1}/2, {d1}/2, {l1}, 32);
                    const mesh1 = new THREE.Mesh(geom1, material3D);
                    mesh1.position.y = {l1}/2;
                    group.add(mesh1);

                    const geom2 = new THREE.CylinderGeometry({d2}/2, {d2}/2, {l2}, 32);
                    const mesh2 = new THREE.Mesh(geom2, material3D);
                    mesh2.position.y = {l1} + {l2}/2;
                    group.add(mesh2);
                }} 
                else if ("{k_type}" === "Pelat Flensa Berlubang (Flange Plate)") {{
                    const shape = new THREE.Shape();
                    shape.absarc(0, 0, {d_outer}/2, 0, Math.PI * 2, false);
                    const holePath = new THREE.Path();
                    holePath.absarc(0, 0, {d_inner}/2, 0, Math.PI * 2, true);
                    shape.holes.push(holePath);

                    const extrudeSettings = {{ depth: {tebal}, bevelEnabled: false }};
                    const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                    const mesh = new THREE.Mesh(geom, material3D);
                    mesh.rotation.x = Math.PI / 2;
                    group.add(mesh);
                }} 
                else {{
                    const boxGeom1 = new THREE.BoxGeometry({p}, {tebal_b}, {l});
                    const mesh1 = new THREE.Mesh(boxGeom1, material3D);
                    group.add(mesh1);

                    const boxGeom2 = new THREE.BoxGeometry({tebal_b}, {t}, {l});
                    const mesh2 = new THREE.Mesh(boxGeom2, material3D);
                    mesh2.position.set(-{p}/2 + {tebal_b}/2, {t}/2, 0);
                    group.add(mesh2);
                }}

                scene.add(group);

                function animate() {{
                    requestAnimationFrame(animate);
                    controls.update();
                    renderer.render(scene, camera);
                }}
                animate();

                window.addEventListener('resize', () => {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }});
            </script>
        </body>
        </html>
        """
        return html_code

    # Render Visualizer 3D dengan Parameter Lengkap
    html_output = render_3d_viewer(komponen_type, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b)
    components.html(html_output, height=420)

with col2:
    st.subheader("📊 Analisis Teknik AI")
    st.metric("Estimasi Berat Total", f"{berat_gram:.2f} Gram")
    st.metric("Total Volume Material", f"{total_volume:.2f} cm³")
    st.metric("Estimasi Biaya Produksi", f"Rp {harga_est:,.0f}")
    
    st.markdown("---")
    st.subheader("💾 Ekspor Model CAD")
    
    # Tombol Ekspor File CAD
    st.download_button(
        label="📥 Download File 3D (STL)",
        data=f"DELUXY.AI CAD MODEL - {komponen_type}\nMaterial: {material}\nVolume: {total_volume:.2f} cm3",
        file_name=f"Deluxy_CAD_{komponen_type.split()[0]}.stl",
        mime="application/slate"
    )
    
    st.download_button(
        label="📥 Download Laporan Spesifikasi (TXT)",
        data=f"=== DELUXY.AI SPECIFICATION REPORT ===\nTipe Komponen: {komponen_type}\nMaterial: {material}\nBerat: {berat_gram:.2f} g\nEstimasi Biaya: Rp {harga_est:,.0f}",
        file_name="Laporan_Spesifikasi_CAD.txt",
        mime="text/plain"
    )

st.markdown("---")
st.info("💡 **Tips AI:** Anda dapat mengubah spesifikasi dimensi pada menu di sebelah kiri, dan pratinjau 3D beserta kalkulasi teknik akan diperbarui secara otomatis.")
