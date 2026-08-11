import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import json
import re
import google.generativeai as genai

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="DELUXY.Ai - Generative Text-to-3D CAD Engine",
    page_icon="🤖",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1565C0;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    .sub-header {
        font-size: 1rem;
        color: #555;
        text-align: center;
        margin-bottom: 25px;
    }
    .ai-badge {
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 DELUXY.Ai - AI Generative CAD Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by Gemini AI - Masukkan prompt bebas dalam bahasa alami</div>', unsafe_allow_html=True)

# ================= SIDEBAR PARAMETER =================
st.sidebar.header("🔑 AI API & Material Setting")

# Input API Key Gemini
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Dapatkan API Key gratis dari Google AI Studio (aistudio.google.com)")

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
    value="tolong buatkan saya komponen dari rel pancing",
    placeholder="Contoh: 'Buatkan komponen internal reel pancing', 'Gear pinion 16 gigi', 'Poros engkol'"
)

# ================= LOGIKA LLM AI PARSER =================
@st.cache_data(show_spinner=False)
def parse_prompt_with_gemini(prompt_text, gemini_key):
    """Menggunakan Gemini AI untuk menganalisis niat client dan menghasilkan parameter CAD"""
    if not gemini_key:
        return None
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt_instruction = f"""
        Anda adalah AI CAD Assistant berpengalaman. Tugas Anda adalah menganalisis permintaan pengguna (bahkan jika ambigu/bebas seperti '{prompt_text}') dan memetakan menjadi salah satu dari 4 bentuk 3D dasar CAD berikut:
        1. "Roda Gigi (Spur Gear)" - Gunakan ini jika permintaan berupa gear, gigi, pinion, drive gear rel pancing, dll.
        2. "Poros Bertingkat (Shaft)" - Gunakan ini jika permintaan berupa poros, as, shaft, main shaft rel pancing, rod, dll.
        3. "Pelat Flensa Berlubang (Flange Plate)" - Gunakan ini untuk disk, rotor plate, piringan rem, penutup melingkar berlubang.
        4. "Siku Penopang (Bracket)" - Gunakan ini untuk rangka L, mount, penopang, casing siku, dll.

        Kembalikan HANYA format JSON valid tanpa tanda backtick/markdown ```json ... ```. Format JSON:
        {{
            "komponen_type": "salah satu dari 4 jenis di atas",
            "penjelasan_ai": "alasan singkat mengapa bentuk ini dipilih berdasarkan permintaan",
            "params": {{
                "num_teeth": 18,
                "gear_radius": 40,
                "gear_thickness": 12,
                "gear_bore": 10,
                "d1": 25,
                "l1": 60,
                "d2": 35,
                "l2": 50,
                "d_outer": 100,
                "d_inner": 30,
                "tebal": 8,
                "jumlah_lubang": 4,
                "d_lubang": 6,
                "p": 70,
                "l": 40,
                "t": 70,
                "tebal_b": 5
            }}
        }}
        """

        response = model.generate_content(prompt_instruction)
        cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_text)
    except Exception as e:
        st.error(f"Gagal memproses dengan AI: {e}")
        return None

# Panggil AI Gemini
ai_result = None
if api_key and user_prompt:
    with st.spinner("🧠 AI Gemini sedang menganalisis permintaan client..."):
        ai_result = parse_prompt_with_gemini(user_prompt, api_key)

# Fallback Cerdas jika API Key belum diisi
if not ai_result:
    prompt_lower = user_prompt.lower()
    if any(kw in prompt_lower for kw in ["pancing", "reel", "shaft", "poros", "as"]):
        komponen_type = "Poros Bertingkat (Shaft)"
        penjelasan = "Terdeteksi kata 'rel pancing/shaft', dipetakan ke Main Shaft (Poros Utama) Rel Pancing."
    elif any(kw in prompt_lower for kw in ["gear", "gigi", "gir"]):
        komponen_type = "Roda Gigi (Spur Gear)"
        penjelasan = "Terdeteksi kata 'gear/gigi', dipetakan ke Roda Gigi (Spur Gear)."
    elif any(kw in prompt_lower for kw in ["flange", "pelat", "piringan"]):
        komponen_type = "Pelat Flensa Berlubang (Flange Plate)"
        penjelasan = "Terdeteksi kata 'flange/pelat', dipetakan ke Pelat Flensa Berlubang."
    else:
        komponen_type = "Siku Penopang (Bracket)"
        penjelasan = "Permintaan umum, dipetakan ke Bracket/Rangka penopang dasar."
    
    params = {}
else:
    komponen_type = ai_result.get("komponen_type", "Poros Bertingkat (Shaft)")
    penjelasan = ai_result.get("penjelasan_ai", "Dipilih berdasarkan analisis AI Gemini.")
    params = ai_result.get("params", {})

# Tampilkan Status AI
st.markdown(f"""
<div class="ai-badge">
    🧠 <b>AI Intent Detector:</b> {penjelasan}<br>
    🎯 <b>Bentuk 3D Terpilih:</b> <u>{komponen_type}</u>
</div>
""", unsafe_allow_html=True)

# Inisialisasi Parameter Berdasarkan Hasil AI
num_teeth = params.get("num_teeth", 18)
gear_radius = params.get("gear_radius", 40)
gear_thickness = params.get("gear_thickness", 12)
gear_bore = params.get("gear_bore", 10)

d1 = params.get("d1", 20)
l1 = params.get("l1", 70)
d2 = params.get("d2", 30)
l2 = params.get("l2", 40)

d_outer = params.get("d_outer", 100)
d_inner = params.get("d_inner", 30)
tebal = params.get("tebal", 8)
jumlah_lubang = params.get("jumlah_lubang", 4)
d_lubang = params.get("d_lubang", 6)

p = params.get("p", 70)
l = params.get("l", 40)
t = params.get("t", 70)
tebal_b = params.get("tebal_b", 5)

# Hitung Volume
if komponen_type == "Roda Gigi (Spur Gear)":
    area_gear = np.pi * (gear_radius/10)**2 * 0.85 - np.pi * ((gear_bore/10)/2)**2
    total_volume = max(0.1, area_gear * (gear_thickness/10))
elif komponen_type == "Poros Bertingkat (Shaft)":
    v1 = np.pi * ((d1/10)/2)**2 * (l1/10)
    v2 = np.pi * ((d2/10)/2)**2 * (l2/10)
    total_volume = v1 + v2
elif komponen_type == "Pelat Flensa Berlubang (Flange Plate)":
    vol_base = np.pi * ((d_outer/10)/2)**2 * (tebal/10)
    vol_hole_center = np.pi * ((d_inner/10)/2)**2 * (tebal/10)
    vol_holes = jumlah_lubang * (np.pi * ((d_lubang/10)/2)**2 * (tebal/10))
    total_volume = max(0.1, vol_base - vol_hole_center - vol_holes)
else:
    total_volume = ((p/10 * l/10 * tebal_b/10) + ((t/10 - tebal_b/10) * l/10 * tebal_b/10))

berat_gram = total_volume * massa_jenis[material]
harga_est = (berat_gram / 1000) * 160000 + 75000

# ================= TAMPILAN VISUALIZER & ANALYSIS =================
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
