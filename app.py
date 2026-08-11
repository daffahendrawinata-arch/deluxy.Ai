import streamlit as st
import streamlit.components.v1 as components
import json
import os
import math
import re
import base64
from html import escape

try:
    import google.generativeai as genai
except Exception:
    genai = None

# ============================================================
# DELUXY.Ai - AI Auto CAD Generator
# V1: Natural language -> structured parameters -> parametric
# mesh -> 3D viewer -> STL export
#
# This version intentionally uses only the packages already in
# requirements.txt:
#   streamlit
#   numpy
#   google-generativeai
#
# STEP export is NOT faked. It is left for a later CAD kernel
# integration (CadQuery/OpenCascade).
# ============================================================

st.set_page_config(
    page_title="DELUXY.Ai - AI Auto CAD Generator",
    page_icon="💎",
    layout="wide",
)

# -------------------- STYLE --------------------
st.markdown(
    """
<style>
.main-title {
    font-size: 2.4rem;
    font-weight: 850;
    background: linear-gradient(90deg, #3B82F6, #8B5CF6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0;
}
.creator-tag {
    text-align: center;
    color: #94A3B8;
    font-weight: 600;
    margin-bottom: 18px;
}
.ai-box,.clarify-box,.error-box,.success-box {
    padding: 14px 18px;
    border-radius: 10px;
    margin: 8px 0 16px;
}
.ai-box {
    background: #172033;
    border-left: 4px solid #3B82F6;
}
.clarify-box {
    background: #211D4A;
    border-left: 4px solid #818CF8;
}
.error-box {
    background: #3A1717;
    border-left: 4px solid #EF4444;
}
.success-box {
    background: #123322;
    border-left: 4px solid #22C55E;
}
.small-muted {
    color: #94A3B8;
    font-size: .86rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# -------------------- MATERIAL DATABASE --------------------
MATERIAL_DB = {
    "Steel": {"density": 7.85, "cost_per_kg": 150000, "mfg": "CNC Turning / Milling"},
    "Stainless Steel": {"density": 8.00, "cost_per_kg": 250000, "mfg": "Precision CNC Turning"},
    "Aluminium": {"density": 2.70, "cost_per_kg": 220000, "mfg": "CNC Machining"},
    "Brass": {"density": 8.40, "cost_per_kg": 300000, "mfg": "Precision Lathe"},
    "Copper": {"density": 8.96, "cost_per_kg": 280000, "mfg": "CNC Machining"},
    "Plastic": {"density": 1.05, "cost_per_kg": 90000, "mfg": "3D Printing / Injection Molding"},
    "Titanium": {"density": 4.50, "cost_per_kg": 950000, "mfg": "5-Axis CNC Machining"},
}

COMPONENT_LABELS = {
    "shaft": "Shaft",
    "stepped_shaft": "Stepped Shaft",
    "cylinder": "Cylinder",
    "flange": "Flange",
    "bolt": "Bolt",
    "bearing": "Bearing",
    "pulley": "Pulley",
    "bracket": "Bracket",
}

# -------------------- SESSION STATE --------------------
DEFAULT_STATE = {
    "status": "empty",
    "component_type": None,
    "units": "mm",
    "material": "Steel",
    "parameters": {},
    "missing_parameters": [],
    "questions": [],
    "last_prompt": "",
    "ai_message": "",
}

if "cad_state" not in st.session_state:
    st.session_state.cad_state = DEFAULT_STATE.copy()
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "model_nonce" not in st.session_state:
    st.session_state.model_nonce = 0


# ============================================================
# UTILITIES
# ============================================================

def get_api_key(sidebar_key: str):
    """Read API key from sidebar, Streamlit secrets, or environment."""
    sidebar_key = (sidebar_key or "").strip()
    if sidebar_key:
        return sidebar_key

    try:
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "").strip() or None


def extract_json(text: str):
    """Extract the first valid JSON object from an AI response."""
    if not text:
        raise ValueError("Respons AI kosong.")

    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise ValueError("AI tidak mengembalikan JSON.")

    depth = 0
    in_string = False
    escaped = False

    for i in range(start, len(cleaned)):
        ch = cleaned[i]

        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start:i + 1]
                return json.loads(candidate)

    raise ValueError("JSON AI tidak lengkap.")


def normalize_number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip().lower()
    s = s.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(match.group()) if match else None


def normalize_units(value):
    value = str(value or "mm").lower().strip()
    aliases = {
        "millimeter": "mm",
        "millimeters": "mm",
        "milimeter": "mm",
        "cm": "cm",
        "centimeter": "cm",
        "centimeters": "cm",
        "inch": "inch",
        "inches": "inch",
        "in": "inch",
        "mm": "mm",
    }
    return aliases.get(value, "mm")


def to_mm(value, units):
    n = normalize_number(value)
    if n is None:
        return None
    if units == "cm":
        return n * 10.0
    if units == "inch":
        return n * 25.4
    return n


def normalize_material(value):
    if not value:
        return "Steel"
    raw = str(value).strip().lower()
    for material in MATERIAL_DB:
        if raw == material.lower():
            return material
    aliases = {
        "stainless": "Stainless Steel",
        "stainless steel": "Stainless Steel",
        "aluminum": "Aluminium",
        "aluminium": "Aluminium",
        "plastic": "Plastic",
    }
    return aliases.get(raw, "Steel")


def canonical_component(value):
    raw = str(value or "").lower().strip()
    aliases = {
        "poros": "shaft",
        "shaft": "shaft",
        "solid shaft": "shaft",
        "stepped shaft": "stepped_shaft",
        "poros bertingkat": "stepped_shaft",
        "cylinder": "cylinder",
        "silinder": "cylinder",
        "flange": "flange",
        "bearing": "bearing",
        "bantalan": "bearing",
        "pulley": "pulley",
        "katrol": "pulley",
        "bolt": "bolt",
        "baut": "bolt",
        "bracket": "bracket",
        "dudukan": "bracket",
    }
    if raw in aliases:
        return aliases[raw]

    for key, result in aliases.items():
        if key in raw:
            return result

    return None


def current_state_for_ai():
    state = st.session_state.cad_state
    return {
        "component_type": state.get("component_type"),
        "units": state.get("units", "mm"),
        "material": state.get("material", "Steel"),
        "parameters": state.get("parameters", {}),
    }


# ============================================================
# AI LAYER
# ============================================================

AI_SYSTEM_PROMPT = r"""
You are the DELUXY.Ai CAD interpretation engine.

Your job is ONLY to translate natural language into structured CAD
parameters. You are NOT a geometry generator.

Return ONLY valid JSON. No markdown. No explanation outside JSON.

Allowed component_type:
shaft, stepped_shaft, cylinder, flange, bolt, bearing, pulley, bracket

Units:
mm, cm, inch

Important rules:
1. Never invent dimensions when the user has not provided them.
2. If a required parameter is missing, return status="needs_clarification".
3. If the user is modifying the current model, preserve the current
   component and all unchanged parameters.
4. Interpret Indonesian and English naturally.
5. Convert obvious dimension expressions such as "12mm", "1.2 cm",
   "setengah inch" when possible.
6. Keep dimensions numeric.
7. For ambiguous requests, ask a concise question.
8. The CAD engine will validate the numbers, so do not output code.

Required parameters:
shaft:
  length, diameter

stepped_shaft:
  overall_length, main_diameter, left_diameter, right_diameter
  hole_diameter is optional

cylinder:
  length, diameter

flange:
  outer_diameter, thickness, hole_diameter

bolt:
  length, shaft_diameter, head_diameter, head_height

bearing:
  outer_diameter, inner_diameter, width

pulley:
  outer_diameter, width, bore_diameter

bracket:
  length, width, height, thickness

JSON schema:
{
  "status": "ready" | "needs_clarification" | "error",
  "component_type": "...",
  "units": "mm",
  "material": "...",
  "parameters": {},
  "missing_parameters": [],
  "questions": [],
  "message": "short Indonesian message"
}
"""


def fallback_analyzer(prompt, current_state):
    """
    Deterministic fallback so the app remains usable when Gemini is
    unavailable. It is deliberately conservative: it only generates
    a model when enough dimensions can be inferred.
    """
    text = prompt.lower()
    current_component = current_state.get("component_type")

    component = canonical_component(text) or current_component

    # Stronger phrase detection.
    if "poros bertingkat" in text or "stepped shaft" in text:
        component = "stepped_shaft"
    elif "poros" in text or "shaft" in text:
        component = "shaft"
    elif "silinder" in text or "cylinder" in text:
        component = "cylinder"

    units = "inch" if ("inch" in text or '"' in text) else ("cm" if "cm" in text else "mm")

    # Extract number immediately associated with common dimension words.
    def find_after(patterns):
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return to_mm(m.group(1), units)
        return None

    length = find_after([
        r"(?:panjang|length)\s*(?:total|utama)?\s*(?:=|:|adalah|jadi)?\s*(\d+(?:[.,]\d+)?)",
        r"(\d+(?:[.,]\d+)?)\s*(?:mm|cm|inch)\s*(?:panjang|length)",
    ])
    diameter = find_after([
        r"(?:diameter|dia|ø|d)\s*(?:utama)?\s*(?:=|:|adalah|jadi)?\s*(\d+(?:[.,]\d+)?)",
        r"(?:diameter utama)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)",
    ])
    left_d = find_after([
        r"(?:diameter kiri|kiri)\s*(?:=|:|adalah)?\s*(\d+(?:[.,]\d+)?)",
    ])
    right_d = find_after([
        r"(?:diameter kanan|kanan)\s*(?:=|:|adalah)?\s*(\d+(?:[.,]\d+)?)",
    ])
    hole_d = find_after([
        r"(?:lubang|hole|bore)\s*(?:tengah|diameter)?\s*(?:=|:|adalah)?\s*(\d+(?:[.,]\d+)?)",
        r"(?:diameter lubang)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)",
    ])

    params = dict(current_state.get("parameters") or {})

    if component in ("shaft", "cylinder"):
        if length is not None:
            params["length"] = length
        if diameter is not None:
            params["diameter"] = diameter

        missing = [x for x in ("length", "diameter") if not normalize_number(params.get(x))]
    elif component == "stepped_shaft":
        if length is not None:
            params["overall_length"] = length
        if diameter is not None:
            params["main_diameter"] = diameter
        if left_d is not None:
            params["left_diameter"] = left_d
        if right_d is not None:
            params["right_diameter"] = right_d
        if hole_d is not None:
            params["hole_diameter"] = hole_d

        missing = [
            x for x in ("overall_length", "main_diameter", "left_diameter", "right_diameter")
            if not normalize_number(params.get(x))
        ]
    else:
        missing = []

    if not component:
        return {
            "status": "needs_clarification",
            "component_type": None,
            "units": units,
            "material": current_state.get("material", "Steel"),
            "parameters": {},
            "missing_parameters": ["component_type"],
            "questions": ["Komponen apa yang ingin dibuat? Contoh: shaft, stepped shaft, cylinder."],
            "message": "Saya belum bisa menentukan jenis komponen.",
        }

    if missing:
        questions_map = {
            "length": "Berapa panjang komponen?",
            "diameter": "Berapa diameter komponen?",
            "overall_length": "Berapa panjang total poros?",
            "main_diameter": "Berapa diameter utama?",
            "left_diameter": "Berapa diameter ujung kiri?",
            "right_diameter": "Berapa diameter ujung kanan?",
        }
        return {
            "status": "needs_clarification",
            "component_type": component,
            "units": "mm",
            "material": current_state.get("material", "Steel"),
            "parameters": params,
            "missing_parameters": missing,
            "questions": [questions_map[x] for x in missing],
            "message": "Saya butuh beberapa ukuran sebelum membuat model.",
        }

    return {
        "status": "ready",
        "component_type": component,
        "units": "mm",
        "material": current_state.get("material", "Steel"),
        "parameters": params,
        "missing_parameters": [],
        "questions": [],
        "message": "Model siap dibuat.",
    }


def analyze_user_request(user_prompt, current_state, api_key):
    """Gemini interprets the request; fallback keeps the app functional."""
    if not api_key or genai is None:
        return fallback_analyzer(user_prompt, current_state)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        context = json.dumps(current_state, ensure_ascii=False)
        prompt = (
            AI_SYSTEM_PROMPT
            + "\nCURRENT CAD STATE:\n"
            + context
            + "\n\nUSER REQUEST:\n"
            + user_prompt
        )

        response = model.generate_content(prompt)
        result = extract_json(response.text)

        if not isinstance(result, dict):
            raise ValueError("Format AI bukan object JSON.")

        result.setdefault("status", "error")
        result.setdefault("parameters", {})
        result.setdefault("missing_parameters", [])
        result.setdefault("questions", [])
        result.setdefault("message", "")

        result["component_type"] = canonical_component(result.get("component_type"))
        result["units"] = normalize_units(result.get("units"))
        result["material"] = normalize_material(result.get("material"))

        # Normalize all numeric parameters.
        for key, value in list(result["parameters"].items()):
            number = normalize_number(value)
            result["parameters"][key] = number if number is not None else value

        return result

    except Exception as exc:
        # Do not crash the app. Try deterministic interpretation.
        fallback = fallback_analyzer(user_prompt, current_state)
        fallback["message"] = (
            fallback.get("message", "")
            + " Gemini tidak tersedia/merespons, jadi DELUXY.Ai memakai mode lokal."
        )
        return fallback


# ============================================================
# VALIDATION
# ============================================================

def validate_parameters(component_type, parameters):
    p = parameters or {}
    errors = []

    def positive(name):
        value = normalize_number(p.get(name))
        if value is None:
            errors.append(f"Parameter '{name}' belum diisi.")
        elif value <= 0:
            errors.append(f"Parameter '{name}' harus lebih besar dari 0.")

    if component_type in ("shaft", "cylinder"):
        positive("length")
        positive("diameter")

    elif component_type == "stepped_shaft":
        for name in ("overall_length", "main_diameter", "left_diameter", "right_diameter"):
            positive(name)

        if p.get("hole_diameter") is not None:
            positive("hole_diameter")

        if not errors:
            L = float(p["overall_length"])
            md = float(p["main_diameter"])
            ld = float(p["left_diameter"])
            rd = float(p["right_diameter"])
            hd = normalize_number(p.get("hole_diameter"))

            if max(ld, rd) > md:
                errors.append("Diameter ujung tidak boleh lebih besar dari diameter utama.")
            if hd is not None and hd >= min(ld, rd):
                errors.append("Diameter lubang harus lebih kecil dari diameter ujung terkecil.")

            # Simple manufacturable length check.
            if L < 10:
                errors.append("Panjang total terlalu kecil untuk V1.")

    elif component_type == "flange":
        for name in ("outer_diameter", "thickness", "hole_diameter"):
            positive(name)
        if not errors and p["hole_diameter"] >= p["outer_diameter"]:
            errors.append("Diameter lubang flange harus lebih kecil dari diameter luar.")

    elif component_type == "bolt":
        for name in ("length", "shaft_diameter", "head_diameter", "head_height"):
            positive(name)

    elif component_type == "bearing":
        for name in ("outer_diameter", "inner_diameter", "width"):
            positive(name)
        if not errors and p["inner_diameter"] >= p["outer_diameter"]:
            errors.append("Diameter dalam bearing harus lebih kecil dari diameter luar.")

    elif component_type == "pulley":
        for name in ("outer_diameter", "width", "bore_diameter"):
            positive(name)
        if not errors and p["bore_diameter"] >= p["outer_diameter"]:
            errors.append("Diameter bore pulley harus lebih kecil dari diameter luar.")

    elif component_type == "bracket":
        for name in ("length", "width", "height", "thickness"):
            positive(name)

    else:
        errors.append("Jenis komponen belum didukung oleh CAD engine V1.")

    return errors


# ============================================================
# PARAMETRIC MESH ENGINE
# Mesh format: vertices + triangular faces.
# Coordinates are in millimeters.
# ============================================================

def cylinder_mesh(radius, length, segments=64, z0=0.0):
    vertices = []
    faces = []

    for z in (z0, z0 + length):
        for i in range(segments):
            a = 2.0 * math.pi * i / segments
            vertices.append((radius * math.cos(a), radius * math.sin(a), z))

    # Side quads -> triangles.
    for i in range(segments):
        j = (i + 1) % segments
        b0, b1 = i, j
        t0, t1 = segments + i, segments + j
        faces.append((b0, b1, t1))
        faces.append((b0, t1, t0))

    # Bottom and top centers.
    bottom_center = len(vertices)
    vertices.append((0.0, 0.0, z0))
    top_center = len(vertices)
    vertices.append((0.0, 0.0, z0 + length))

    for i in range(segments):
        j = (i + 1) % segments
        faces.append((bottom_center, j, i))
        faces.append((top_center, segments + i, segments + j))

    return vertices, faces


def stepped_shaft_mesh(p, segments=64):
    L = float(p["overall_length"])
    md = float(p["main_diameter"]) / 2.0
    ld = float(p["left_diameter"]) / 2.0
    rd = float(p["right_diameter"]) / 2.0
    hole = normalize_number(p.get("hole_diameter"))

    # Divide the length into 20% / 60% / 20%.
    l1 = L * 0.20
    l2 = L * 0.60
    l3 = L - l1 - l2

    sections = [
        (0.0, l1, ld),
        (l1, l2, md),
        (l1 + l2, l3, rd),
    ]

    vertices = []
    faces = []

    # If hollow, generate a ring-based mesh for each section.
    inner_r = (hole / 2.0) if hole else 0.0

    # Create rings at every section boundary.
    boundaries = [
        (0.0, ld),
        (l1, ld),
        (l1, md),
        (l1 + l2, md),
        (l1 + l2, rd),
        (L, rd),
    ]

    ring_indices = []
    for z, r in boundaries:
        outer = []
        inner = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            outer.append(len(vertices))
            vertices.append((r * math.cos(a), r * math.sin(a), z))

        if inner_r > 0:
            for i in range(segments):
                a = 2 * math.pi * i / segments
                inner.append(len(vertices))
                vertices.append((inner_r * math.cos(a), inner_r * math.sin(a), z))

        ring_indices.append((outer, inner))

    # Connect adjacent rings.
    for k in range(len(ring_indices) - 1):
        o0, i0 = ring_indices[k]
        o1, i1 = ring_indices[k + 1]

        for i in range(segments):
            j = (i + 1) % segments
            faces.append((o0[i], o0[j], o1[j]))
            faces.append((o0[i], o1[j], o1[i]))

            if inner_r > 0:
                faces.append((i0[i], i1[j], i0[j]))
                faces.append((i0[i], i1[i], i1[j]))

    if inner_r <= 0:
        # Cap ends.
        c0 = len(vertices)
        vertices.append((0, 0, 0))
        c1 = len(vertices)
        vertices.append((0, 0, L))
        o0 = ring_indices[0][0]
        o1 = ring_indices[-1][0]
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((c0, o0[j], o0[i]))
            faces.append((c1, o1[i], o1[j]))
    else:
        # Annular end caps.
        o0, i0 = ring_indices[0]
        o1, i1 = ring_indices[-1]
        for i in range(segments):
            j = (i + 1) % segments
            faces.append((o0[i], o0[j], i0[j]))
            faces.append((o0[i], i0[j], i0[i]))
            faces.append((o1[i], i1[j], o1[j]))
            faces.append((o1[i], i1[i], i1[j]))

    return vertices, faces


def make_mesh(component_type, p):
    if component_type == "shaft":
        return cylinder_mesh(float(p["diameter"]) / 2, float(p["length"]))

    if component_type == "cylinder":
        return cylinder_mesh(float(p["diameter"]) / 2, float(p["length"]))

    if component_type == "stepped_shaft":
        return stepped_shaft_mesh(p)

    if component_type == "flange":
        # Flange with a through bore.
        outer = float(p["outer_diameter"]) / 2
        inner = float(p["hole_diameter"]) / 2
        length = float(p["thickness"])
        seg = 64
        vertices = []
        faces = []

        for z in (0.0, length):
            for r in (outer, inner):
                for i in range(seg):
                    a = 2 * math.pi * i / seg
                    vertices.append((r * math.cos(a), r * math.sin(a), z))

        # Index layout: bottom outer, bottom inner, top outer, top inner.
        bo, bi, to, ti = 0, seg, 2 * seg, 3 * seg
        for i in range(seg):
            j = (i + 1) % seg
            faces += [
                (bo + i, bo + j, to + j),
                (bo + i, to + j, to + i),
                (bi + i, ti + j, bi + j),
                (bi + i, ti + i, ti + j),
                (bo + i, bi + j, bo + j),
                (bo + i, bi + i, bi + j),
                (to + i, to + j, ti + j),
                (to + i, ti + j, ti + i),
            ]
        return vertices, faces

    if component_type == "bolt":
        # Approximate bolt: shaft + cylindrical head.
        shaft_p = {"diameter": p["shaft_diameter"], "length": p["length"]}
        v1, f1 = cylinder_mesh(float(p["shaft_diameter"]) / 2, float(p["length"]), 48)
        v2, f2 = cylinder_mesh(
            float(p["head_diameter"]) / 2,
            float(p["head_height"]),
            48,
            float(p["length"]),
        )
        offset = len(v1)
        return v1 + v2, f1 + [tuple(idx + offset for idx in face) for face in f2]

    if component_type == "bearing":
        # Ring mesh.
        return make_ring_mesh(
            float(p["outer_diameter"]) / 2,
            float(p["inner_diameter"]) / 2,
            float(p["width"]),
        )

    if component_type == "pulley":
        return make_ring_mesh(
            float(p["outer_diameter"]) / 2,
            float(p["bore_diameter"]) / 2,
            float(p["width"]),
        )

    if component_type == "bracket":
        return make_box_mesh(
            float(p["length"]),
            float(p["width"]),
            float(p["height"]),
        )

    raise ValueError("Komponen belum didukung.")


def make_ring_mesh(outer_r, inner_r, length, segments=64):
    vertices = []
    faces = []
    # bottom outer, bottom inner, top outer, top inner
    for z in (0.0, length):
        for r in (outer_r, inner_r):
            for i in range(segments):
                a = 2 * math.pi * i / segments
                vertices.append((r * math.cos(a), r * math.sin(a), z))

    bo, bi, to, ti = 0, segments, 2 * segments, 3 * segments
    for i in range(segments):
        j = (i + 1) % segments
        faces.extend([
            (bo + i, bo + j, to + j),
            (bo + i, to + j, to + i),
            (bi + i, ti + j, bi + j),
            (bi + i, ti + i, ti + j),
            (bo + i, bi + j, bo + j),
            (bo + i, bi + i, bi + j),
            (to + i, to + j, ti + j),
            (to + i, ti + j, ti + i),
        ])
    return vertices, faces


def make_box_mesh(length, width, height):
    x = length / 2
    y = width / 2
    z = height / 2
    vertices = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
    ]
    faces = [
        (0, 1, 2), (0, 2, 3),
        (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1),
        (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3),
        (3, 7, 4), (3, 4, 0),
    ]
    return vertices, faces


def mesh_volume_mm3(vertices, faces):
    # Signed tetrahedron volume around origin.
    total = 0.0
    for a, b, c in faces:
        ax, ay, az = vertices[a]
        bx, by, bz = vertices[b]
        cx, cy, cz = vertices[c]
        total += (
            ax * (by * cz - bz * cy)
            - ay * (bx * cz - bz * cx)
            + az * (bx * cy - by * cx)
        ) / 6.0
    return abs(total)


# ============================================================
# STL EXPORT
# ============================================================

def normal(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / length, ny / length, nz / length


def mesh_to_ascii_stl(vertices, faces, name="DELUXY_Ai"):
    lines = [f"solid {name}"]
    for face in faces:
        a, b, c = (vertices[face[0]], vertices[face[1]], vertices[face[2]])
        nx, ny, nz = normal(a, b, c)
        lines.append(f"  facet normal {nx:.7g} {ny:.7g} {nz:.7g}")
        lines.append("    outer loop")
        for v in (a, b, c):
            lines.append(f"      vertex {v[0]:.7g} {v[1]:.7g} {v[2]:.7g}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {name}")
    return ("\n".join(lines) + "\n").encode("utf-8")


# ============================================================
# 3D VIEWER - THREE.JS CDN
# ============================================================

def render_3d_view(vertices, faces, title="DELUXY.Ai Model"):
    # Keep HTML payload compact.
    payload = {
        "vertices": [[round(x, 5), round(y, 5), round(z, 5)] for x, y, z in vertices],
        "faces": [list(f) for f in faces],
    }
    data = json.dumps(payload, separators=(",", ":"))

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
html,body,#viewer {{
    width:100%; height:100%; margin:0; padding:0;
    overflow:hidden; background:#0b1020;
    font-family:Arial,sans-serif;
}}
#label {{
    position:fixed; top:10px; left:12px; z-index:5;
    color:#cbd5e1; font-size:13px; font-weight:600;
    background:rgba(15,23,42,.72); padding:7px 10px;
    border-radius:7px;
}}
</style>
</head>
<body>
<div id="viewer"></div>
<div id="label">{escape(title)}</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const DATA = {data};

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0b1020);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.01, 100000);
camera.position.set(180, 140, 180);

const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setPixelRatio(window.devicePixelRatio || 1);
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById("viewer").appendChild(renderer.domElement);

const ambient = new THREE.HemisphereLight(0xffffff, 0x223344, 1.5);
scene.add(ambient);

const key = new THREE.DirectionalLight(0xffffff, 2.2);
key.position.set(150, 200, 250);
scene.add(key);

const geom = new THREE.BufferGeometry();
const pos = [];
for (const f of DATA.faces) {{
    for (const idx of f) {{
        const v = DATA.vertices[idx];
        pos.push(v[0], v[1], v[2]);
    }}
}}
geom.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
geom.computeVertexNormals();

const material = new THREE.MeshStandardMaterial({{
    color:0x5b9cff,
    metalness:0.42,
    roughness:0.28,
    side:THREE.DoubleSide
}});
const mesh = new THREE.Mesh(geom, material);
scene.add(mesh);

const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(geom, 35),
    new THREE.LineBasicMaterial({{color:0x9ec5ff, transparent:true, opacity:.24}})
);
scene.add(edges);

// Fit camera to object.
const box = new THREE.Box3().setFromObject(mesh);
const center = box.getCenter(new THREE.Vector3());
const size = box.getSize(new THREE.Vector3());
mesh.position.sub(center);
edges.position.copy(mesh.position);

const maxDim = Math.max(size.x, size.y, size.z);
camera.position.set(maxDim*1.35, maxDim*0.95, maxDim*1.35);
camera.lookAt(0,0,0);

// Simple mouse orbit controls without another dependency.
let dragging=false, lastX=0, lastY=0, rotX=-0.25, rotY=0.7, dist=Math.max(maxDim*2.2, 80);

function updateCamera(){{
    camera.position.x = Math.sin(rotY)*Math.cos(rotX)*dist;
    camera.position.y = Math.sin(rotX)*dist;
    camera.position.z = Math.cos(rotY)*Math.cos(rotX)*dist;
    camera.lookAt(0,0,0);
}}
updateCamera();

renderer.domElement.addEventListener("mousedown", e=>{{
    dragging=true; lastX=e.clientX; lastY=e.clientY;
}});
window.addEventListener("mouseup", ()=>dragging=false);
window.addEventListener("mousemove", e=>{{
    if(!dragging) return;
    rotY -= (e.clientX-lastX)*0.008;
    rotX -= (e.clientY-lastY)*0.008;
    rotX=Math.max(-1.45,Math.min(1.45,rotX));
    lastX=e.clientX; lastY=e.clientY;
    updateCamera();
}});
renderer.domElement.addEventListener("wheel", e=>{{
    e.preventDefault();
    dist *= Math.exp(e.deltaY*0.001);
    dist=Math.max(maxDim*0.35,Math.min(maxDim*10,dist));
    updateCamera();
}}, {{passive:false}});

let touchX=0,touchY=0;
renderer.domElement.addEventListener("touchstart",e=>{{
    if(e.touches.length===1){{touchX=e.touches[0].clientX;touchY=e.touches[0].clientY;}}
}});
renderer.domElement.addEventListener("touchmove",e=>{{
    if(e.touches.length!==1)return;
    rotY-=(e.touches[0].clientX-touchX)*0.008;
    rotX-=(e.touches[0].clientY-touchY)*0.008;
    rotX=Math.max(-1.45,Math.min(1.45,rotX));
    touchX=e.touches[0].clientX;touchY=e.touches[0].clientY;
    updateCamera();
}});

window.addEventListener("resize",()=>{{
    camera.aspect=window.innerWidth/window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth,window.innerHeight);
}});

function animate(){{
    requestAnimationFrame(animate);
    renderer.render(scene,camera);
}}
animate();
</script>
</body>
</html>
"""
    components.html(html, height=560, scrolling=False)


# ============================================================
# UI / SIDEBAR
# ============================================================

st.markdown('<div class="main-title">💎 DELUXY.Ai</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="creator-tag">AI Auto CAD Generator • Parametric CAD V1</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ DELUXY.Ai")

    api_input = st.text_input(
        "Gemini API Key",
        type="password",
        help="Bisa dikosongkan jika GEMINI_API_KEY sudah disimpan di Streamlit Secrets.",
    )
    api_key = get_api_key(api_input)

    st.divider()

    material_options = list(MATERIAL_DB.keys())
    current_material = st.session_state.cad_state.get("material", "Steel")
    material = st.selectbox(
        "Material",
        material_options,
        index=material_options.index(current_material)
        if current_material in material_options
        else 0,
    )
    st.session_state.cad_state["material"] = material

    units = st.selectbox(
        "Unit",
        ["mm", "cm", "inch"],
        index=["mm", "cm", "inch"].index(
            st.session_state.cad_state.get("units", "mm")
        ),
    )
    st.session_state.cad_state["units"] = units

    st.divider()

    if st.button("🗑️ Reset CAD", use_container_width=True):
        st.session_state.cad_state = DEFAULT_STATE.copy()
        st.session_state.conversation_history = []
        st.session_state.model_nonce += 1
        st.rerun()

    st.caption("V1 fokus pada parameter → geometry → STL.")
    if api_key:
        st.success("Gemini siap digunakan.")
    else:
        st.info("Mode lokal aktif. Tambahkan Gemini API Key untuk pemahaman bahasa yang lebih kuat.")


# ============================================================
# MAIN PROMPT
# ============================================================

state = st.session_state.cad_state
active = state.get("component_type")

st.subheader("🧠 Apa yang ingin kamu buat?")

with st.form("cad_prompt_form", clear_on_submit=True):
    prompt = st.text_area(
        "Instruksi CAD",
        placeholder=(
            "Contoh: buat poros bertingkat panjang 120mm, "
            "diameter utama 20mm, ujung kiri 12mm, ujung kanan 15mm, "
            "lubang tengah 6mm"
        ),
        height=110,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("🚀 Generate / Update CAD", use_container_width=True)

if submitted:
    prompt = prompt.strip()
    if not prompt:
        st.warning("Masukkan instruksi terlebih dahulu.")
    else:
        current = current_state_for_ai()
        result = analyze_user_request(prompt, current, api_key)

        st.session_state.conversation_history.append({
            "role": "user",
            "content": prompt,
        })

        if result.get("status") == "ready":
            component = canonical_component(result.get("component_type"))
            params = result.get("parameters") or {}

            # Normalize units to mm internally.
            ai_units = normalize_units(result.get("units"))
            normalized = {}
            for key, value in params.items():
                n = normalize_number(value)
                if n is not None:
                    normalized[key] = to_mm(n, ai_units)
                else:
                    normalized[key] = value

            errors = validate_parameters(component, normalized)

            if errors:
                result["status"] = "error"
                result["missing_parameters"] = []
                result["questions"] = []
                result["message"] = "Parameter tidak valid."

                st.session_state.cad_state.update({
                    "status": "error",
                    "component_type": component,
                    "units": "mm",
                    "material": normalize_material(result.get("material") or material),
                    "parameters": normalized,
                    "missing_parameters": [],
                    "questions": errors,
                    "last_prompt": prompt,
                    "ai_message": result["message"],
                })
            else:
                st.session_state.cad_state.update({
                    "status": "ready",
                    "component_type": component,
                    "units": "mm",
                    "material": normalize_material(result.get("material") or material),
                    "parameters": normalized,
                    "missing_parameters": [],
                    "questions": [],
                    "last_prompt": prompt,
                    "ai_message": result.get("message", "Model siap."),
                })
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": result.get("message", "Model berhasil diperbarui."),
                })
                st.session_state.model_nonce += 1

        elif result.get("status") == "needs_clarification":
            # Preserve current parameters and merge whatever AI understood.
            merged = dict(state.get("parameters") or {})
            incoming = result.get("parameters") or {}
            for key, value in incoming.items():
                n = normalize_number(value)
                merged[key] = to_mm(n, normalize_units(result.get("units"))) if n is not None else value

            st.session_state.cad_state.update({
                "status": "needs_clarification",
                "component_type": canonical_component(result.get("component_type")) or active,
                "units": "mm",
                "material": normalize_material(result.get("material") or material),
                "parameters": merged,
                "missing_parameters": result.get("missing_parameters", []),
                "questions": result.get("questions", []),
                "last_prompt": prompt,
                "ai_message": result.get("message", "Informasi belum lengkap."),
            })
        else:
            st.session_state.cad_state.update({
                "status": "error",
                "last_prompt": prompt,
                "ai_message": result.get("message", "Terjadi kesalahan."),
                "questions": result.get("questions", []),
            })

        st.rerun()


# ============================================================
# CURRENT STATE
# ============================================================

state = st.session_state.cad_state
component_type = state.get("component_type")
params = state.get("parameters") or {}
material = state.get("material", "Steel")

if state.get("status") == "needs_clarification":
    st.markdown(
        '<div class="clarify-box"><b>💡 DELUXY.Ai membutuhkan beberapa informasi.</b></div>',
        unsafe_allow_html=True,
    )
    for question in state.get("questions", []):
        st.write("• " + question)

elif state.get("status") == "error":
    st.markdown(
        '<div class="error-box"><b>❌ Parameter belum valid.</b></div>',
        unsafe_allow_html=True,
    )
    for question in state.get("questions", []):
        st.write("• " + question)

elif component_type:
    st.markdown(
        f'<div class="success-box"><b>✓ {escape(COMPONENT_LABELS.get(component_type, component_type))}</b> siap dibuat.</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# PARAMETER EDITOR
# ============================================================

if component_type:
    st.subheader("📐 CAD Parameters")

    editable = {}
    for key, value in params.items():
        if isinstance(value, (int, float)) and value is not None:
            editable[key] = st.number_input(
                key.replace("_", " ").title() + " (mm)",
                min_value=0.01,
                value=float(value),
                step=0.5,
                key=f"param_{key}",
            )

    if editable:
        if st.button("🔄 Apply Parameter Changes", use_container_width=True):
            new_params = dict(params)
            new_params.update(editable)
            errors = validate_parameters(component_type, new_params)

            if errors:
                st.error(" / ".join(errors))
            else:
                st.session_state.cad_state["parameters"] = new_params
                st.session_state.cad_state["status"] = "ready"
                st.session_state.model_nonce += 1
                st.success("Parameter berhasil diperbarui.")
                st.rerun()


# ============================================================
# GENERATE / VIEW MODEL
# ============================================================

if component_type and state.get("status") == "ready":
    errors = validate_parameters(component_type, params)

    if errors:
        st.error(" / ".join(errors))
    else:
        try:
            vertices, faces = make_mesh(component_type, params)
            volume = mesh_volume_mm3(vertices, faces)

            density = MATERIAL_DB.get(material, MATERIAL_DB["Steel"])["density"]
            mass_grams = volume / 1000.0 * density
            estimated_cost = mass_grams / 1000.0 * MATERIAL_DB.get(
                material, MATERIAL_DB["Steel"]
            )["cost_per_kg"]

            st.subheader("🧊 3D Model")
            render_3d_view(
                vertices,
                faces,
                f"{COMPONENT_LABELS.get(component_type, component_type)} • {material}",
            )

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Component", COMPONENT_LABELS.get(component_type, component_type))
            col2.metric("Volume", f"{volume:,.1f} mm³")
            col3.metric("Weight", f"{mass_grams:,.2f} g")
            col4.metric("Est. Material", f"Rp {estimated_cost:,.0f}")

            st.subheader("🏭 Engineering Information")
            info1, info2 = st.columns(2)

            with info1:
                st.write("**Material:**", material)
                st.write("**Manufacturing:**", MATERIAL_DB[material]["mfg"])
                st.write("**Internal unit:** mm")

            with info2:
                st.write("**Vertices:**", len(vertices))
                st.write("**Triangles:**", len(faces))
                st.write("**Geometry:** Parametric mesh")

            st.subheader("⬇️ Export")

            stl_data = mesh_to_ascii_stl(
                vertices,
                faces,
                name=f"DELUXY_{component_type}",
            )

            filename = f"deluxy_{component_type}.stl"
            st.download_button(
                "⬇️ Download STL",
                data=stl_data,
                file_name=filename,
                mime="model/stl",
                use_container_width=True,
            )

            st.info(
                "STL V1 sudah berupa mesh geometry nyata. "
                "STEP belum diaktifkan agar DELUXY.Ai tidak mengirim file STEP palsu. "
                "STEP akan ditambahkan saat kita memasang CAD kernel OpenCascade/CadQuery."
            )

        except Exception as exc:
            st.error(f"Gagal membuat geometry: {exc}")


# ============================================================
# CONVERSATION
# ============================================================

if st.session_state.conversation_history:
    with st.expander("💬 Conversation / CAD History", expanded=False):
        for item in st.session_state.conversation_history[-12:]:
            role = "👤 User" if item["role"] == "user" else "🤖 DELUXY.Ai"
            st.markdown(f"**{role}:** {item['content']}")

