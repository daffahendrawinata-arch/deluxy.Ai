import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import json
import google.generativeai as genai

# Page Config
st.set_page_config(
    page_title="DELUXY.Ai - AI CAD Engine",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 DELUXY.Ai - AI Auto CAD Generator")
st.write("Ketik komponen apa saja, AI akan otomatis memilihkan dan menampilkan bentuk 3D yang paling sesuai.")

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Pengaturan AI & Material")
api_key = st.sidebar.text_input("Masukkan Gemini API Key:", type="password", help="Bisa dikosongkan jika ingin pakai mode deteksi otomatis bawaan.")

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

# ================= INPUT USER =================
user_prompt = st.text_input(
    "Apa yang ingin Anda buat?",
    value="tolong buatkan saya komponen dari rel pancing"
)

# ================= LOGIKA UTAMA (AI KENDALIKAN PILIHAN BENTUK) =================
def tentukan_bentuk_by_ai(prompt, key):
    # Jika API Key diisi, AI Gemini yang mengambil keputusan penuh
    if key:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt_system = f"""
            Pengguna meminta: '{prompt}'
            Pilihlah SATU dari 4 jenis bentuk 3D berikut yang paling cocok:
            1. "Roda Gigi (Spur Gear)" -> jika berhubungan dengan gear, gigi, pinion.
            2. "Poros Bertingkat (Shaft)" -> jika berhubungan dengan rel pancing, as, shaft, rod, pancingan.
            3. "Pelat Flensa Berlubang (Flange Plate)" -> jika berhubungan dengan disk, piringan, flange, plate.
            4. "Siku Penopang (Bracket)" -> jika berhubungan dengan bracket, siku, dudukan, mount.

            Jawab HANYA dalam format JSON berikut tanpa teks lain:
            {{
                "bentuk": "nama bentuk terpilih",
                "alasan": "alasan singkat AI memilih bentuk ini"
            }}
            """
            res = model.generate_content(prompt_system)
            clean_res = res.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_res)
            return data["bentuk"], data["alasan"]
        except Exception as e:
            st.warning(f"AI Key error/tidak valid, berpindah ke Mode Auto-Deteksi Kata Kunci. ({e})")

    # Mode Auto-Deteksi bawaan (Backup jika tanpa API Key)
    p_lower = prompt.lower()
    if any(k in p_lower for k in ["pancing", "reel", "shaft", "poros", "as", "rod"]):
        return "Poros Bertingkat (Shaft)", "Terdeteksi kata pancing/poros, AI memilihkan model Poros Rel Pancing (Main Shaft)."
    elif any(k in p_lower for k in ["gear", "gigi", "gir", "pinion"]):
        return "Roda Gigi (Spur Gear)", "Terdeteksi kata gear/gigi, AI memilihkan model Roda Gigi."
    elif any(k in p_lower for k in ["flange", "pelat", "piringan", "disk"]):
        return "Pelat Flensa Berlubang (Flange Plate)", "Terdeteksi kata pelat/flange, AI memilihkan model Pelat Berlubang."
    else:
        return "Siku Penopang (Bracket)", "AI memilihkan model Bracket Siku Penopang Universal."

# Jalankan Penentuan Bentuk
bentuk_terpilih, alasan_ai = tentukan_bentuk_by_ai(user_prompt, api_key)

st.info(f"💡 **Keputusan AI:** {alasan_ai}")

# ================= RENDER 3D CANVAS =================
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader(f"🖼️ Gambar/Model 3D: {bentuk_terpilih}")

    def generate_3d_html(jenis, mat_color):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            <style> body {{ margin: 0; overflow: hidden; background: #0e1117; }} canvas {{ width: 100%; height: 100%; }} </style>
        </head>
        <body>
            <script>
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(80, 80, 120);

                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                renderer.setSize(window.innerWidth, window.innerHeight);
                document.body.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;

                scene.add(new THREE.AmbientLight(0xffffff, 0.7));
                const light = new THREE.DirectionalLight(0xffffff, 1);
                light.position.set(50, 100, 50);
                scene.add(light);

                scene.add(new THREE.GridHelper(200, 20, 0x444444, 0x222222));

                const material = new THREE.MeshStandardMaterial({{ color: {mat_color}, metalness: 0.8, roughness: 0.3 }});
                const group = new THREE.Group();

                if ("{jenis}" === "Poros Bertingkat (Shaft)") {{
                    // Model Poros / Shaft
                    const s1 = new THREE.Mesh(new THREE.CylinderGeometry(8, 8, 80, 32), material);
                    s1.position.y = 40;
                    const s2 = new THREE.Mesh(new THREE.CylinderGeometry(14, 14, 30, 32), material);
                    s2.position.y = 95;
                    group.add(s1);
                    group.add(s2);
                }} else if ("{jenis}" === "Roda Gigi (Spur Gear)") {{
                    // Model Gear
                    const gearGeom = new THREE.CylinderGeometry(35, 35, 12, 18);
                    const mesh = new THREE.Mesh(gearGeom, material);
                    group.add(mesh);
                }} else if ("{jenis}" === "Pelat Flensa Berlubang (Flange Plate)") {{
                    // Model Flange
                    const plate = new THREE.Mesh(new THREE.CylinderGeometry(40, 40, 8, 32), material);
                    group.add(plate);
                }} else {{
                    // Model Bracket
                    const b1 = new THREE.Mesh(new THREE.BoxGeometry(60, 6, 40), material);
                    const b2 = new THREE.Mesh(new THREE.BoxGeometry(6, 60, 40), material);
                    b2.position.set(-27, 30, 0);
                    group.add(b1);
                    group.add(b2);
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

    components.html(generate_3d_html(bentuk_terpilih, warna_render[material]), height=480)

with col2:
    st.subheader("📊 Info Output")
    st.write(f"**Item Terpilih:** {bentuk_terpilih}")
    st.write(f"**Material:** {material}")
    st.success("Visualisasi 3D berhasil dirender oleh AI!")
