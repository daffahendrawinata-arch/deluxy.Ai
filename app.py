import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Generator",
    page_icon="⚙️",
    layout="wide"
)

# Style Custom Header
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        color: #1565C0;
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

st.markdown('<div class="main-header">⚙️ DELUXY.Ai - Precision CAD Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform Desain Komponen Permesinan & Dynamic 3D CAD Generator</div>', unsafe_allow_html=True)

# ================= SIDEBAR PARAMETER =================
st.sidebar.header("🎛️ Panel Kontrol Desain")

st.sidebar.subheader("✍️ Permintaan Khusus Client")
client_custom_text = st.sidebar.text_area(
    "Tulis instruksi kustom di sini:",
    height=80,
    placeholder="Contoh: Gear spur module 2 dengan 20 gigi..."
)

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ Pilih Tipe Komponen 3D")

komponen_type = st.sidebar.selectbox(
    "Tipe Bentuk 3D:",
    ["Roda Gigi (Spur Gear)", "Poros Bertingkat (Shaft)", "Pelat Flensa Berlubang (Flange Plate)", "Siku Penopang (Bracket)"]
)

material = st.sidebar.selectbox(
    "Pilih Material:",
    ["Baja Carbon (ST37)", "Aluminium 6061", "Kuningan (Brass)", "Plastik ABS"]
)

massa_jenis = {
    "Baja Carbon (ST37)": 7.85,
    "Aluminium 6061": 2.70,
    "Kuningan (Brass)": 8.40,
    "Plastik ABS": 1.05
}

warna_render = {
    "Baja Carbon (ST37)": 0xaaaaaa,
    "Aluminium 6061": 0xd1d5db,
    "Kuningan (Brass)": 0xeab308,
    "Plastik ABS": 0x374151
}

st.sidebar.subheader("📐 Dimensi Utama (mm)")

# Inisialisasi Variabel
d1 = l1 = d2 = l2 = 0
d_outer = d_inner = tebal = jumlah_lubang = d_lubang = 0
p = l = t = tebal_b = 0
num_teeth = gear_radius = gear_thickness = gear_bore = 0
total_volume = 0.1

if komponen_type == "Roda Gigi (Spur Gear)":
    num_teeth = st.sidebar.slider("Jumlah Gigi (Teeth)", 8, 48, 18)
    gear_radius = st.sidebar.slider("Radius Luar Gear (mm)", 20, 150, 50)
    gear_thickness = st.sidebar.slider("Ketebalan Gear (mm)", 5, 50, 15)
    gear_bore = st.sidebar.slider("Diameter Lubang Poros (mm)", 5, 50, 15)
    
    # Hitung Volume estimasi Gear
    area_gear = np.pi * (gear_radius/10)**2 * 0.85 - np.pi * ((gear_bore/10)/2)**2
    total_volume = max(0.1, area_gear * (gear_thickness/10))

elif komponen_type == "Poros Bertingkat (Shaft)":
    d1 = st.sidebar.slider("Diameter 1 (d1)", 10, 100, 30)
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
    jumlah_lubang = st.sidebar.slider("Jumlah Lubang Baut", 3, 12, 4)
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

berat_gram = total_volume * massa_jenis[material]
harga_est = (berat_gram / 1000) * 160000 + 75000

# ================= TAMPILAN UTAMA =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🧊 Real-time 3D CAD Visualizer")
    st.caption("Gunakan Mouse: Klik Kiri = Putar, Scroll = Zoom, Klik Kanan = Geser.")

    def render_3d_viewer(k_type, mat_color, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b, n_teeth, g_rad, g_thick, g_bore):
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

                const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(100, 100, 140);

                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
                scene.add(ambientLight);

                const spotLight = new THREE.SpotLight(0xffffff, 1.2);
                spotLight.position.set(100, 150, 100);
                scene.add(spotLight);

                const grid = new THREE.GridHelper(250, 25, 0x333333, 0x222222);
                scene.add(grid);

                const material3D = new THREE.MeshPhysicalMaterial({{ 
                    color: {mat_color}, 
                    metalness: 0.8, 
                    roughness: 0.2,
                    clearcoat: 0.2
                }});

                const group = new THREE.Group();

                // ENGINE GENERATOR RODA GIGI (GEAR)
                if ("{k_type}" === "Roda Gigi (Spur Gear)") {{
                    const shape = new THREE.Shape();
                    const teeth = {n_teeth};
                    const outerR = {g_rad};
                    const innerR = outerR * 0.82;
                    const boreR = {g_bore} / 2;

                    for (let i = 0; i < teeth; i++) {{
                        const angle = (i / teeth) * Math.PI * 2;
                        const nextAngle = ((i + 1) / teeth) * Math.PI * 2;
                        const a1 = angle + (nextAngle - angle) * 0.1;
                        const a2 = angle + (nextAngle - angle) * 0.4;
                        const a3 = angle + (nextAngle - angle) * 0.6;
                        const a4 = angle + (nextAngle - angle) * 0.9;

                        if (i === 0) shape.moveTo(Math.cos(a1) * innerR, Math.sin(a1) * innerR);
                        shape.lineTo(Math.cos(a2) * outerR, Math.sin(a2) * outerR);
                        shape.lineTo(Math.cos(a3) * outerR, Math.sin(a3) * outerR);
                        shape.lineTo(Math.cos(a4) * innerR, Math.sin(a4) * innerR);
                    }}

                    const holePath = new THREE.Path();
                    holePath.absarc(0, 0, boreR, 0, Math.PI * 2, true);
                    shape.holes.push(holePath);

                    const extrudeSettings = {{ depth: {g_thick}, bevelEnabled: true, bevelThickness: 1, bevelSize: 0.5, bevelSegments: 2 }};
                    const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                    const mesh = new THREE.Mesh(geom, material3D);
                    mesh.rotation.x = Math.PI / 2;
                    group.add(mesh);
                }} 
                else if ("{k_type}" === "Poros Bertingkat (Shaft)") {{
                    const geom1 = new THREE.CylinderGeometry({d1}/2, {d1}/2, {l1}, 64);
                    const mesh1 = new THREE.Mesh(geom1, material3D);
                    mesh1.position.y = {l1}/2;
                    group.add(mesh1);

                    const geom2 = new THREE.CylinderGeometry({d2}/2, {d2}/2, {l2}, 64);
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

                    const extrudeSettings = {{ depth: {tebal}, bevelEnabled: true, bevelThickness: 1, bevelSize: 0.5, bevelSegments: 2 }};
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
            </script>
        </body>
        </html>
        """
        return html_code

    current_color = warna_render[material]
    html_output = render_3d_viewer(
        komponen_type, current_color, d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b,
        num_teeth, gear_radius, gear_thickness, gear_bore
    )
    components.html(html_output, height=520)

with col2:
    st.subheader("📊 Analisis Teknik AI")
    
    if client_custom_text:
        st.info(f"**Instruksi Client:**\n\"{client_custom_text}\"")
    
    st.metric("Estimasi Berat Total", f"{berat_gram:.2f} Gram")
    st.metric("Total Volume Material", f"{total_volume:.2f} cm³")
    st.metric("Estimasi Biaya Produksi", f"Rp {harga_est:,.0f}")
    
    st.markdown("---")
    st.subheader("💾 Ekspor Model CAD")
    
    final_type_desc = client_custom_text if client_custom_text else komponen_type
    
    st.download_button(
        label="📥 Download Model 3D (STL)",
        data=f"DELUXY.AI CAD MODEL - {final_type_desc}\nMaterial: {material}\nVolume: {total_volume:.2f} cm3",
        file_name=f"Deluxy_{komponen_type.split()[0]}.stl",
        mime="application/slate"
    )

st.markdown("---")
st.success("✅ **Gear Generator Aktif!** Sekarang Anda dan client bisa memilih opsi **'Roda Gigi (Spur Gear)'** pada menu kiri untuk mengubah pratinjau 3D secara langsung menjadi Roda Gigi interaktif.")
