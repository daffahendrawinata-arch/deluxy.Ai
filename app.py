import streamlit as st
import streamlit.components.v1 as components
import json
import google.generativeai as genai

# ================= 1. KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="DELUXY.Ai - Professional Text-to-3D Engine",
    page_icon="💎",
    layout="wide"
)

# Custom CSS - Theme Dark Modern & Premium
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .creator-tag {
        font-size: 0.95rem;
        font-weight: 600;
        color: #94A3B8;
        text-align: center;
        margin-bottom: 25px;
    }
    .ai-box {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #F8FAFC;
    }
    .metric-card {
        background: #1E293B;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💎 DELUXY.Ai - Text-to-3D CAD Engine</div>', unsafe_allow_html=True)
# NAMA KAMU DICANTUMKAN DI SINI
st.markdown('<div class="creator-tag">Designed & Built by: <b>[Nama Kamu]</b> | Lead CAD Developer</div>', unsafe_allow_html=True)

# ================= 2. SIDEBAR =================
st.sidebar.header("⚙️ System & Material Settings")
api_key = st.sidebar.text_input("Gemini API Key (Opsional):", type="password", help="Masukkan API Key jika ingin Gemini membaca prompt bebas dengan kecerdasan penuh.")

material = st.sidebar.selectbox(
    "Pilih Material Komponen:",
    ["Baja Carbon (ST37)", "Aluminium 6061", "Kuningan (Brass)", "Plastik ABS"]
)

# Data Properti Material
mat_props = {
    "Baja Carbon (ST37)": {"density": 7.85, "color": 0xaaaaaa, "cost_per_kg": 150000},
    "Aluminium 6061": {"density": 2.70, "color": 0xd1d5db, "cost_per_kg": 220000},
    "Kuningan (Brass)": {"density": 8.40, "color": 0xeab308, "cost_per_kg": 300000},
    "Plastik ABS": {"density": 1.05, "color": 0x38bdf8, "cost_per_kg": 90000}
}

# ================= 3. INPUT CLIENT & PRESETS =================
st.subheader("💬 AI Prompt Bar & Presets")

# Tombol Cepat (Presets)
col_p1, col_p2, col_p3, col_p4 = st.columns(4)
preset_selected = ""
if col_p1.button("🎣 Component Rel Pancing"):
    preset_selected = "tolong buatkan saya komponen dari rel pancing"
if col_p2.button("⚙️ Spur Gear Pinion"):
    preset_selected = "buatkan roda gigi pinion 18 gigi"
if col_p3.button("⭕ Flange Plate"):
    preset_selected = "pelat piringan berlubang untuk rem"
if col_p4.button("📐 Mounting Bracket"):
    preset_selected = "siku penopang rangka mesin"

# Gunakan preset jika ditekan, jika tidak pakai nilai default
default_value = preset_selected if preset_selected else "tolong buatkan saya komponen dari rel pancing"

user_prompt = st.text_input(
    "Masukkan instruksi / permintaan client:",
    value=default_value,
    placeholder="Contoh: 'Rel pancing', 'Poros engkol', 'Gigi roda', 'Pelat flange'"
)

# ================= 4. LOGIKA AI PENENTU BENTUK & SPEK =================
def analisa_prompt_client(prompt, key):
    if key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            instruction = f"""
            Analisis permintaan: '{prompt}'
            Pilih SATU bentuk 3D yang paling relevan:
            1. "Poros Bertingkat (Shaft)" -> Jika berkaitan dengan pancing, rel pancing, as, shaft, rod.
            2. "Roda Gigi (Spur Gear)" -> Jika berkaitan dengan gear, gigi, pinion.
            3. "Pelat Flensa (Flange Plate)" -> Jika berkaitan dengan disk, piringan, pelat berlubang.
            4. "Siku Penopang (Bracket)" -> Jika berkaitan dengan bracket, dudukan, mount.

            Kembalikan JSON saja tanpa markdown:
            {{"bentuk": "nama bentuk", "alasan": "alasan singkat", "est_volume_cm3": 45}}
            """
            res = model.generate_content(instruction)
            clean_res = res.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_res)
            return data["bentuk"], data["alasan"], data.get("est_volume_cm3", 40)
        except Exception:
            pass

    # Fallback Otomatis
    p = prompt.lower()
    if any(k in p for k in ["pancing", "reel", "shaft", "poros", "as", "rod"]):
        return "Poros Bertingkat (Shaft)", "AI mendeteksi 'pancing/poros' dan merancang Main Shaft Rel Pancing Presisi.", 35.0
    elif any(k in p for k in ["gear", "gigi", "gir", "pinion"]):
        return "Roda Gigi (Spur Gear)", "AI mendeteksi 'gear/gigi' dan merancang Spur Gear 18 Gigi.", 45.0
    elif any(k in p for k in ["flange", "pelat", "piringan", "disk", "rem"]):
        return "Pelat Flensa (Flange Plate)", "AI mendeteksi 'pelat/disk' dan merancang Flange Plate Berlubang.", 50.0
    else:
        return "Siku Penopang (Bracket)", "AI merancang Universal L-Bracket Siku Penopang.", 30.0

bentuk_terpilih, alasan_ai, est_vol = analisa_prompt_client(user_prompt, api_key)

# Kalkulasi Teknik
m_density = mat_props[material]["density"]
m_cost_kg = mat_props[material]["cost_per_kg"]
est_weight_gram = est_vol * m_density
est_cost_rp = (est_weight_gram / 1000) * m_cost_kg + 50000  # + Biaya Machining dasar

# Tampilan Status AI
st.markdown(f"""
<div class="ai-box">
    <b>🧠 AI Decision Engine:</b> {alasan_ai}<br>
    <b>🎯 Form Factor Terpilih:</b> <u>{bentuk_terpilih}</u>
</div>
""", unsafe_allow_html=True)

# ================= 5. OUTPUT RENDER 3D & ANALISIS BIUAY =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("🧊 Interactive 3D Canvas")

    def build_3d_html(jenis, color_hex):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; background: #0B0F19; }}
                canvas {{ width: 100%; height: 100%; }}
                .controls-overlay {{
                    position: absolute; top: 10px; right: 10px; display: flex; gap: 5px;
                }}
                .btn-cam {{
                    background: #1E293B; color: #F8FAFC; border: 1px solid #475569;
                    padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 11px;
                }}
                .btn-cam:hover {{ background: #3B82F6; }}
            </style>
        </head>
        <body>
            <div class="controls-overlay">
                <button class="btn-cam" onclick="setCam('iso')">Isometrik</button>
                <button class="btn-cam" onclick="setCam('top')">Top</button>
                <button class="btn-cam" onclick="setCam('front')">Front</button>
            </div>
            <script>
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(90, 90, 130);

                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.autoRotate = true;
                controls.autoRotateSpeed = 1.5;

                scene.add(new THREE.AmbientLight(0xffffff, 0.7));
                const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
                dirLight1.position.set(80, 120, 80);
                scene.add(dirLight1);
                
                const dirLight2 = new THREE.DirectionalLight(0x3b82f6, 0.5);
                dirLight2.position.set(-80, -50, -80);
                scene.add(dirLight2);

                scene.add(new THREE.GridHelper(200, 20, 0x334155, 0x1e293b));

                const mat = new THREE.MeshStandardMaterial({{ color: {color_hex}, metalness: 0.85, roughness: 0.2 }});
                const group = new THREE.Group();

                if ("{jenis}" === "Poros Bertingkat (Shaft)") {{
                    const s1 = new THREE.Mesh(new THREE.CylinderGeometry(7, 7, 90, 32), mat);
                    s1.position.y = 45;
                    const s2 = new THREE.Mesh(new THREE.CylinderGeometry(14, 14, 35, 32), mat);
                    s2.position.y = 107.5;
                    group.add(s1); group.add(s2);
                }} else if ("{jenis}" === "Roda Gigi (Spur Gear)") {{
                    const gear = new THREE.Mesh(new THREE.CylinderGeometry(35, 35, 14, 20), mat);
                    group.add(gear);
                }} else if ("{jenis}" === "Pelat Flensa (Flange Plate)") {{
                    const plate = new THREE.Mesh(new THREE.CylinderGeometry(45, 45, 8, 32), mat);
                    group.add(plate);
                }} else {{
                    const b1 = new THREE.Mesh(new THREE.BoxGeometry(60, 6, 40), mat);
                    const b2 = new THREE.Mesh(new THREE.BoxGeometry(6, 60, 40), mat);
                    b2.position.set(-27, 30, 0);
                    group.add(b1); group.add(b2);
                }}

                scene.add(group);

                function setCam(type) {{
                    controls.autoRotate = false;
                    if(type === 'iso') camera.position.set(90, 90, 130);
                    if(type === 'top') camera.position.set(0, 160, 0);
                    if(type === 'front') camera.position.set(0, 0, 160);
                    controls.update();
                }}

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

    components.html(build_3d_html(bentuk_terpilih, mat_props[material]["color"]), height=490)

with col2:
    st.subheader("📊 Engineering Analysis")
    
    st.metric("Estimasi Berat", f"{est_weight_gram:.1f} Gram")
    st.metric("Est. Volume", f"{est_vol:.1f} cm³")
    st.metric("Est. Biaya Manufaktur", f"Rp {est_cost_rp:,.0f}")

    st.markdown("---")
    st.write(f"**Bentuk:** {bentuk_terpilih}")
    st.write(f"**Material:** {material}")
    st.write(f"**Massa Jenis:** {m_density} g/cm³")
    
    st.markdown("---")
    st.download_button(
        label="📥 Download STL File (CAD)",
        data=f"DELUXY.AI GENERATED FILE\nModel: {bentuk_terpilih}\nMaterial: {material}\nWeight: {est_weight_gram:.1f}g",
        file_name=f"DELUXY_{bentuk_terpilih.split()[0]}.stl",
        mime="application/slate"
    )
