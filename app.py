import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import re

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DELUXY.Ai - Text-to-3D CAD Engine",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling
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
    .ai-badge {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 DELUXY.Ai - Dynamic Text-to-3D CAD</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ketik perintah client di bawah, AI akan langsung membuat model 3D CAD yang sesuai!</div>', unsafe_allow_html=True)

# ================= SIDEBAR PARAMETER =================
st.sidebar.header("🎨 Pengaturan Material & AI")

material = st.sidebar.selectbox(
    "Pilih Material Komponen:",
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

# ================= KOTAK PROMPT AI (INPUT UTAMA) =================
st.subheader("💬 AI Prompt Bar")
user_prompt = st.text_input(
    "Masukkan instruksi / permintaan client:",
    value="Tolong buatkan Roda Gigi (Gear) dengan 20 gigi dan tebal 20mm",
    placeholder="Contoh: 'Buatkan saya poros bertingkat', 'Tolong gambarkan gear 12 gigi', atau 'Buat flange plate 4 lubang'"
)

# ================= LOGIKA DETEKSI / ENGINE AI =================
prompt_lower = user_prompt.lower()

# AI Parsing logic untuk menentukan Tipe Komponen
if any(kw in prompt_lower for kw in ["gear", "gigi", "roda gigi", "cog", "pinion"]):
    komponen_type = "Roda Gigi (Spur Gear)"
elif any(kw in prompt_lower for kw in ["poros", "shaft", "as ", "rod", "silinder bertingkat"]):
    komponen_type = "Poros Bertingkat (Shaft)"
elif any(kw in prompt_lower for kw in ["flange", "flensa", "pelat bulat", "piringan berlubang", "disk"]):
    komponen_type = "Pelat Flensa Berlubang (Flange Plate)"
elif any(kw in prompt_lower for kw in ["bracket", "siku", "penopang", "l-bracket", "dudukan"]):
    komponen_type = "Siku Penopang (Bracket)"
else:
    # Default jika kata kunci tidak dikenali
    komponen_type = "Roda Gigi (Spur Gear)"

st.markdown(f"""
<div class="ai-badge">
    🧠 <b>AI Intent Detector:</b> Terdeteksi client meminta bentuk <b>{komponen_type}</b>.
</div>
""", unsafe_allow_html=True)

# Ekstraksi angka otomatis jika pengguna menyebutkan jumlah gigi di prompt
extracted_numbers = re.findall(r'\d+', prompt_lower)
default_teeth = int(extracted_numbers[0]) if extracted_numbers and komponen_type == "Roda Gigi (Spur Gear)" else 18
default_teeth = max(8, min(default_teeth, 48))

# Fine-tuning slider opsional di Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📐 Precision Adjuster (AI Fine-Tune)")

# Dynamic UI Sidebar sesuai komponen yang dideteksi AI
if komponen_type == "Roda Gigi (Spur Gear)":
    num_teeth = st.sidebar.slider("Jumlah Gigi (Teeth)", 8, 48, default_teeth)
    gear_radius = st.sidebar.slider("Radius Luar Gear (mm)", 20, 150, 50)
    gear_thickness = st.sidebar.slider("Ketebalan Gear (mm)", 5, 50, 15)
    gear_bore = st.sidebar.slider("Diameter Lubang Poros (mm)", 5, 50, 15)
    
    area_gear = np.pi * (gear_radius/10)**2 * 0.85 - np.pi * ((gear_bore/10)/2)**2
    total_volume = max(0.1, area_gear * (gear_thickness/10))
    d1 = l1 = d2 = l2 = d_outer = d_inner = tebal = jumlah_lubang = d_lubang = p = l = t = tebal_b = 0

elif komponen_type == "Poros Bertingkat (Shaft)":
    d1 = st.sidebar.slider("Diameter 1 (d1)", 10, 100, 30)
    l1 = st.sidebar.slider("Panjang 1 (l1)", 20, 200, 50)
    d2 = st.sidebar.slider("Diameter 2 (d2)", 10, 100, 45)
    l2 = st.sidebar.slider("Panjang 2 (l2)", 20, 200, 80)
    
    v1 = np.pi * ((d1/10)/2)**2 * (l1/10)
    v2 = np.pi * ((d2/10)/2)**2 * (l2/10)
    total_volume = v1 + v2
    num_teeth = gear_radius = gear_thickness = gear_bore = d_outer = d_inner = tebal = jumlah_lubang = d_lubang = p = l = t = tebal_b = 0

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
    num_teeth = gear_radius = gear_thickness = gear_bore = d1 = l1 = d2 = l2 = p = l = t = tebal_b = 0

else: # Bracket
    p = st.sidebar.slider("Panjang (P)", 30, 200, 80)
    l = st.sidebar.slider("Lebar (L)", 20, 150, 50)
    t = st.sidebar.slider("Tinggi (T)", 30, 200, 80)
    tebal_b = st.sidebar.slider("Tebal Dinding (t)", 3, 20, 6)
    
    total_volume = ((p/10 * l/10 * tebal_b/10) + ((t/10 - tebal_b/10) * l/10 * tebal_b/10))
    num_teeth = gear_radius = gear_thickness = gear_bore = d1 = l1 = d2 = l2 = d_outer = d_inner = tebal = jumlah_lubang = d_lubang = 0

berat_gram = total_volume * massa_jenis[material]
harga_est = (berat_gram / 1000) * 160000 + 75000

# ================= TAMPILAN VISUALIZER & EYES =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🧊 Output Canvas 3D AI")

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
                scene.background = new THREE.Color(0x111827);

                const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(100, 100, 140);

                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.shadowMap.enabled = true;
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
                scene.add(ambientLight);

                const spotLight = new THREE.SpotLight(0xffffff, 1.2);
                spotLight.position.set(100, 150, 100);
                scene.add(spotLight);

                const grid = new THREE.GridHelper(250, 25, 0x374151, 0x1f2937);
                scene.add(grid);

                const material3D = new THREE.MeshPhysicalMaterial({{ 
                    color: {mat_color}, 
                    metalness: 0.8, 
                    roughness: 0.2,
                    clearcoat: 0.3
                }});

                const group = new THREE.Group();

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

    html_output = render_3d_viewer(
        komponen_type, warna_render[material], d1, l1, d2, l2, d_outer, d_inner, tebal, p, l, t, tebal_b,
        num_teeth, gear_radius, gear_thickness, gear_bore
    )
    components.html(html_output, height=520)

with col2:
    st.subheader("📊 Analisis Teknik AI")
    st.metric("Bentuk Terdeteksi", komponen_type)
    st.metric("Estimasi Berat", f"{berat_gram:.2f} Gram")
    st.metric("Volume Material", f"{total_volume:.2f} cm³")
    st.metric("Estimasi Biaya Produksi", f"Rp {harga_est:,.0f}")
    
    st.markdown("---")
    st.download_button(
        label="📥 Download STL File (CAD)",
        data=f"DELUXY.AI GENERATED CAD\nPrompt: {user_prompt}\nType: {komponen_type}\nMaterial: {material}",
        file_name=f"Deluxy_AI_{komponen_type.split()[0]}.stl",
        mime="application/slate"
    )
