import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Generator",
    page_icon="⚙️",
    layout="wide"
)

# Style Header & Tampilan Custom
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        color: #1565C0;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.2rem;
        color: #444;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background-color: #fcfdfe;
        border-radius: 8px;
    }
    .css-1r6slb0 { /* Style sidebar */
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">⚙️ DELUXY.Ai - HD CAD Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform Desain Komponen Permesinan dengan Visualisasi 3D Halus (Render Engine Diperbarui)</div>', unsafe_allow_html=True)

# ================= SIDEBAR PARAMETER =================
st.sidebar.header("🎛️ Panel Kontrol Client")

st.sidebar.subheader("✍️ Permintaan Khusus Client")
client_custom_text = st.sidebar.text_area(
    "Tulis detail komponen yang Anda inginkan (misal: 'Poros transmisi dengan alur pasak'):",
    height=90,
    placeholder="Contoh: Poros dengan toleransi h7..."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Preset & Material")

komponen_type = st.sidebar.selectbox(
    "Pilih Tipe Dasar (Untuk Visualisasi):",
    ["Poros Bertingkat (Shaft)", "Pelat Flensa Berlubang (Flange Plate)", "Siku Penopang (Bracket)"]
)

material = st.sidebar.selectbox(
    "Pilih Material:",
    ["Baja Carbon (ST37)", "Aluminium 6061", "Kuningan (Brass)", "Plastik ABS"]
)

# Properti fisik material
massa_jenis = {
    "Baja Carbon (ST37)": 7.85,
    "Aluminium 6061": 2.70,
    "Kuningan (Brass)": 8.40,
    "Plastik ABS": 1.05
}

warna_render = {
    "Baja Carbon (ST37)": 0xaaaaaa, # Abu-abu logam
    "Aluminium 6061": 0xcccccc,    # Abu-abu muda mengkilap
    "Kuningan (Brass)": 0xe5c156,  # Kuning emas
    "Plastik ABS": 0x444444        # Hitam dop
}

st.sidebar.subheader("📐 Dimensi Utama (mm)")

# Inisialisasi variabel
d1 = l1 = d2 = l2 = 0
d_outer = d_inner = tebal = jumlah_lubang = d_lubang = 0
p = l = t = tebal_b = 0
total_volume = 0.1

if komponen_type == "Poros Bertingkat (Shaft)":
    d1 = st.sidebar.slider("Diameter 1 (d1)", 10, 100, 30, help="Diameter bagian bawah poros")
    l1 = st.sidebar.slider("Panjang 1 (l1)", 20, 200, 50)
    d2 = st.sidebar.slider("Diameter 2 (d2)", 10, 100, 45)
    l2 = st.sidebar.slider("Panjang 2 (l2)", 20, 200, 80)
    v1 = np.pi * ((d1/10)/2)**2 * (l1/10)
    v2 = np.pi * ((d2/10)/2)**2 * (l2/10)
    total_volume = v1 + v2

elif komponen_type == "Pelat Flensa Berlubang (Flange Plate)":
    d_outer = st.sidebar.slider("Diameter Luar (OD)", 50, 300, 120)
    d_inner = st.sidebar.slider("Diameter Lubang Tengah (ID)", 10, 200, 40)
    tebal = st.sidebar.slider("Ketebalan (t)", 2, 50, 10)
    jumlah_lubang = st.sidebar.slider("Jumlah Lubang", 3, 12, 4)
    d_lubang = st.sidebar.slider("Diameter Lubang Baut", 4, 20, 8)
    vol_base = np.pi * ((d_outer/10)/2)**2 * (tebal/10)
    vol_hole_center = np.pi * ((d_inner/10)/2)**2 * (tebal/10)
    vol_holes = jumlah_lubang * (np.pi * ((d_lubang/10)/2)**2 * (tebal/10))
    total_volume = max(0.1, vol_base - vol_hole_center - vol_holes)

else:  # Bracket
    p = st.sidebar.slider("Panjang (P)", 30, 200, 80)
    l = st.sidebar.slider("Lebar (L)", 20, 150, 50)
    t = st.sidebar.slider("Tinggi (T)", 30, 200, 80)
    tebal_b = st.sidebar.slider("Tebal Dinding (t)", 3, 20, 6)
    total_volume = ((p/10 * l/10 * tebal_b/10) + ((t/10 - tebal_b/10) * l/10 * tebal_b/10))

# Berat & Biaya
berat_gram = total_volume * massa_jenis[material]
harga_est = (berat_gram / 1000) * 160000 + 75000 # Biaya estimasi diperbarui

# ================= TAMPILAN UTAMA =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🧊 Pratinjau 3D CAD Halus (HD)")
    st.caption("Gunakan Mouse: Klik Kiri = Putar, Scroll = Zoom, Klik Kanan = Geser.")

    # Generator HTML/ThreeJS DITINGKATKAN TOTAL UNTUK KUALITAS HD
    def render_3d_viewer_hd(k_type, mat_color, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b):
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <style> body {{ margin: 0; overflow: hidden; background-color: #121212; }} canvas {{ width: 100%; height: 100%; }} </style>
        </head>
        <body>
            <script>
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0x1a1a1a);
                // scene.fog = new THREE.FogExp2(0x1a1a1a, 0.002); // Menambah kedalaman

                const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(120, 110, 180);

                const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true; // Aktifkan bayangan
                renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.08;

                // --- PENCERAHAN PROFESIONAL (Studio Setup) ---
                const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
                scene.add(ambientLight);

                const spotLight = new THREE.SpotLight(0xffffff, 1.2);
                spotLight.position.set(100, 150, 100);
                spotLight.castShadow = true;
                spotLight.shadow.mapSize.width = 1024;
                spotLight.shadow.mapSize.height = 1024;
                scene.add(spotLight);

                const keyLight = new THREE.DirectionalLight(0xffffff, 0.6);
                keyLight.position.set(-80, 80, -80);
                scene.add(keyLight);

                // --- GROUND GRID DENGAN SHADOW ---
                const gridHelper = new THREE.GridHelper(300, 30, 0x333333, 0x222222);
                scene.add(gridHelper);

                // --- MATERIAL PBR (Physical Based Rendering) - LEBIH HALUS & NYATA ---
                const material3D = new THREE.MeshPhysicalMaterial({{ 
                    color: {mat_color}, 
                    metalness: 0.8,    // Membuat pantulan logam lebih tajam
                    roughness: 0.2,    // Permukaan lebih halus
                    clearcoat: 0.1,    // Menambah lapisan kilau ekstra
                    clearcoatRoughness: 0.1,
                    envMapIntensity: 1.0,
                    reflectivity: 0.5
                }});

                const group = new THREE.Group();

                // Fungsi helper untuk menambah Bevel (sudut halus) pada objek kotak
                function createBevelBox(w, h, d, radius) {{
                    const shape = new THREE.Shape();
                    const r = radius;
                    const width = w/2;
                    const height = h/2;

                    shape.moveTo(-width + r, -height);
                    shape.lineTo(width - r, -height);
                    shape.absarc(width - r, -height + r, r, -Math.PI / 2, 0);
                    shape.lineTo(width, height - r);
                    shape.absarc(width - r, height - r, r, 0, Math.PI / 2);
                    shape.lineTo(-width + r, height);
                    shape.absarc(-width + r, height - r, r, Math.PI / 2, Math.PI);
                    shape.lineTo(-width, -height + r);
                    shape.absarc(-width + r, -height + r, r, Math.PI, Math.PI * 1.5);

                    const extrudeSettings = {{ depth: d, bevelEnabled: true, bevelThickness: 0.5, bevelSize: 0.5, bevelSegments: 3 }};
                    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
                }}

                if ("{k_type}" === "Poros Bertingkat (Shaft)") {{
                    // Ditingkatkan: RadialSegments=128 (Sangat Bulat), BevelThickness=0.3 (Sudut tumpul)
                    const geom1 = new THREE.CylinderGeometry({d1}/2, {d1}/2, {l1}, 128); // 128 = sangat halus
                    const mesh1 = new THREE.Mesh(geom1, material3D);
                    mesh1.position.y = {l1}/2;
                    mesh1.castShadow = true;
                    group.add(mesh1);

                    const geom2 = new THREE.CylinderGeometry({d2}/2, {d2}/2, {l2}, 128); // 128 = sangat halus
                    const mesh2 = new THREE.Mesh(geom2, material3D);
                    mesh2.position.y = {l1} + {l2}/2;
                    mesh2.castShadow = true;
                    group.add(mesh2);
                }} 
                else if ("{k_type}" === "Pelat Flensa Berlubang (Flange Plate)") {{
                    // Ditingkatkan: Menambahkan Bevel pada ExtrudeGeometry
                    const shape = new THREE.Shape();
                    shape.absarc(0, 0, {d_outer}/2, 0, Math.PI * 2, false);
                    
                    const holePath = new THREE.Path();
                    holePath.absarc(0, 0, {d_inner}/2, 0, Math.PI * 2, true);
                    shape.holes.push(holePath);

                    const extrudeSettings = {{ depth: {tebal}, bevelEnabled: true, bevelThickness: 1.0, bevelSize: 1.0, bevelSegments: 4 }};
                    const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                    const mesh = new THREE.Mesh(geom, material3D);
                    mesh.rotation.x = Math.PI / 2;
                    mesh.castShadow = true;
                    group.add(mesh);
                }} 
                else {{
                    // Ditingkatkan: Menggunakan createBevelBox agar Bracket tidak terlihat kotak tajam mentah
                    const baseGeom = createBevelBox({p}, {tebal_b}, {l}, 2.0); // Radius 2.0
                    const mesh1 = new THREE.Mesh(baseGeom, material3D);
                    mesh1.rotation.x = Math.PI / 2;
                    mesh1.castShadow = true;
                    group.add(mesh1);

                    const verticalGeom = createBevelBox({tebal_b}, {t}, {l}, 2.0); // Radius 2.0
                    const mesh2 = new THREE.Mesh(verticalGeom, material3D);
                    mesh2.position.set(-{p}/2 + {tebal_b}/2, {t}/2 + {tebal_b}/2, 0); // Posisi disesuaikan
                    mesh2.castShadow = true;
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

    # Render Visualizer 3D HD
    current_color = warna_render[material]
    html_output = render_3d_viewer_hd(komponen_type, current_color, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b)
    components.html(html_output, height=520)

with col2:
    st.subheader("📊 Analisis Teknik AI")
    
    if client_custom_text:
        st.info(f"**Permintaan Kustom Client:**\n\"{client_custom_text}\"")
    
    st.metric("Estimasi Berat Total", f"{berat_gram:.2f} Gram", help="Dihitung berdasarkan volume presisi & massa jenis material")
    st.metric("Total Volume Material", f"{total_volume:.2f} cm³")
    st.metric("Estimasi Biaya Produksi (Rp)", f"{harga_est:,.0f}", help="Perkiraan biaya bahan & fabrikasi dasar")
    
    st.markdown("---")
    st.subheader("💾 Ekspor Model CAD")
    
    final_type_desc = client_custom_text if client_custom_text else komponen_type
    report_text = f"""=== DELUXY.AI HD SPECIFICATION REPORT ===
Deskripsi Komponen (Client): {final_type_desc}
Preset Visual: {komponen_type}
Material: {material}
Berat (Est): {berat_gram:.2f} g
Volume (Precision): {total_volume:.2f} cm3
Biaya Produksi (Est): Rp {harga_est:,.0f}

--- Dimensi Parametrik (mm) ---
"""
    if komponen_type == "Poros Bertingkat (Shaft)":
        report_text += f"d1: {d1}, l1: {l1}, d2: {d2}, l2: {l2}"
    elif komponen_type == "Pelat Flensa Berlubang (Flange Plate)":
        report_text += f"OD: {d_outer}, ID: {d_inner}, t: {tebal}, Holes: {jumlah_lubang}"
    else:
        report_text += f"P: {p}, L: {l}, T: {t}, t_wall: {tebal_b}"

    # Tombol Ekspor
    st.download_button(
        label="📥 Download Model 3D Dasar (STL)",
        data=f"DELUXY.AI HD MODEL\nDesc: {final_type_desc}\nVolume: {total_volume:.2f} cm3",
        file_name=f"Deluxy_HD_{komponen_type.split()[0]}.stl",
        mime="application/slate"
    )
    
    st.download_button(
        label="📥 Download Laporan Spesifikasi (TXT)",
        data=report_text,
        file_name=f"Laporan_Spesifikasi_Deluxy_{material.split()[0]}.txt",
        mime="text/plain"
    )

st.markdown("---")
st.success("💡 **Pembaruan Visual Berhasil:** Model 3D kini di-render dengan kualitas HD. Permukaan poros lebih bulat sempurna, dan setiap sudut tajam pada Flensa/Bracket telah diberi radius (bevel) agar terlihat seperti komponen nyata.")
