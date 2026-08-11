import streamlit as st
import streamlit.components.v1 as components
import json
import os
import math
import google.generativeai as genai

# ================= 1. SYSTEM CONFIGURATION & STYLES =================
st.set_page_config(
    page_title="DELUXY.Ai - AI Auto CAD Generator",
    page_icon="💎",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .creator-tag {
        font-size: 0.9rem;
        font-weight: 600;
        color: #94A3B8;
        text-align: center;
        margin-bottom: 20px;
    }
    .ai-box {
        background-color: #1E293B;
        border-left: 4px solid #3B82F6;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #F8FAFC;
    }
    .clarify-box {
        background-color: #312E81;
        border-left: 4px solid #818CF8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #EEF2FF;
    }
    .error-box {
        background-color: #451A1A;
        border-left: 4px solid #EF4444;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #FEE2E2;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 2. SESSION STATE INITIALIZATION =================
if "cad_state" not in st.session_state:
    st.session_state.cad_state = {
        "status": "ready",
        "component_type": "stepped_shaft",
        "units": "mm",
        "material": "Steel",
        "parameters": {
            "overall_length": 120.0,
            "main_diameter": 12.0,
            "left_diameter": 8.0,
            "right_diameter": 10.0,
            "hole_diameter": 5.0
        },
        "missing_parameters": [],
        "questions": []
    }

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Database Properti Material
MATERIAL_DB = {
    "Steel": {"density": 7.85, "color": "0xaaaaaa", "cost_per_kg": 150000, "mfg": "CNC Turning / Milling"},
    "Stainless Steel": {"density": 8.00, "color": "0xd1d5db", "cost_per_kg": 250000, "mfg": "Precision CNC Turning"},
    "Aluminium": {"density": 2.70, "color": "0xe2e8f0", "cost_per_kg": 220000, "mfg": "CNC Machining"},
    "Brass": {"density": 8.40, "color": "0xeab308", "cost_per_kg": 300000, "mfg": "Precision Lathe"},
    "Copper": {"density": 8.96, "color": "0xb45309", "cost_per_kg": 280000, "mfg": "CNC Machining"},
    "Plastic": {"density": 1.05, "color": "0x38bdf8", "cost_per_kg": 90000, "mfg": "3D Printing / Injection Molding"},
    "Titanium": {"density": 4.50, "color": "0x64748b", "cost_per_kg": 950000, "mfg": "5-Axis CNC Machining"}
}

# ================= 3. HELPER FUNCTIONS =================

def get_api_key(sidebar_key):
    """Mendapatkan API Key dari Secrets, Env Var, atau Sidebar Input."""
    if sidebar_key.strip():
        return sidebar_key.strip()
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ.get("GEMINI_API_KEY")
    return None

def analyze_user_request(user_prompt, current_state, api_key):
    """Menggunakan Gemini untuk menganalisis prompt pengguna dan mengembalikan Structured CAD JSON."""
    if not api_key:
        # Fallback offline heuristic jika API key tidak ada
        p = user_prompt.lower()
        if "poros" in p or "shaft" in p or "pancing" in p:
            return {
                "status": "ready",
                "component_type": "stepped_shaft",
                "units": "mm",
                "material": "Steel",
                "parameters": {
                    "overall_length": 120.0,
                    "main_diameter": 12.0,
                    "left_diameter": 8.0,
                    "right_diameter": 10.0,
                    "hole_diameter": 5.0
                },
                "missing_parameters": [],
                "questions": []
            }
        elif "flange" in p or "piringan" in p or "pelat" in p:
            return {
                "status": "ready",
                "component_type": "flange",
                "units": "mm",
                "material": "Steel",
                "parameters": {
                    "outer_diameter": 80.0,
                    "inner_diameter": 20.0,
                    "thickness": 10.0,
                    "hole_diameter": 6.0
                },
                "missing_parameters": [],
                "questions": []
            }
        else:
            return {
                "status": "ready",
                "component_type": "cylinder",
                "units": "mm",
                "material": "Steel",
                "parameters": {
                    "height": 50.0,
                    "diameter": 30.0,
                    "hole_diameter": 0.0
                },
                "missing_parameters": [],
                "questions": []
            }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        system_instruction = f"""
        Anda adalah CAD Assistant Engine untuk DELUXY.Ai.
        Tugas Anda: Ubah permintaan bahasa alami pengguna menjadi JSON CAD terstruktur.
        
        State CAD saat ini:
        {json.dumps(current_state)}
        
        Komponen yang didukung V1:
        - shaft (parameters: length, diameter, hole_diameter)
        - stepped_shaft (parameters: overall_length, main_diameter, left_diameter, right_diameter, hole_diameter)
        - cylinder (parameters: height, diameter, hole_diameter)
        - flange (parameters: outer_diameter, inner_diameter, thickness, hole_diameter)

        Aturan Output:
        1. Kembalikan HANYA JSON valid tanpa teks penjelas atau markdown codeblock (no ```json).
        2. Jika user ingin mengubah model yang aktif, perbarui nilai parameter yang relevan dari state saat ini.
        3. Jika informasi penting belum ada (misal user hanya berkata 'buatkan poros'), set status menjadi "needs_clarification", isi missing_parameters dan questions.
        4. Jika parameter cukup, set status menjadi "ready".
        5. Nilai parameter HARUS berupa angka floating point / float.

        Format JSON Wajib:
        {{
            "status": "ready" atau "needs_clarification",
            "component_type": "nama_komponen",
            "units": "mm",
            "material": "Steel / Stainless Steel / Aluminium / Brass / Copper / Plastic / Titanium",
            "parameters": {{ ... }},
            "missing_parameters": [...],
            "questions": [...]
        }}
        """
        
        response = model.generate_content([system_instruction, f"User prompt: {user_prompt}"])
        clean_json = response.text.replace("
