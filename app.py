import os
import re
import json
import math
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

try:
    import cadquery as cq
    CAD_AVAILABLE = True
except Exception:
    cq = None
    CAD_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except Exception:
    OpenAI = None
    OPENAI_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DELUXY.Ai",
    page_icon="💎",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .deluxy-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .deluxy-subtitle {
        color: #64748b;
        font-size: 17px;
        margin-top: 5px;
        margin-bottom: 25px;
    }

    .status-card {
        padding: 12px;
        border-radius: 12px;
        background: #0f172a;
        color: white;
        margin-bottom: 10px;
    }

    .ai-card {
        padding: 18px;
        border-radius: 14px;
        background: #eff6ff;
        border-left: 5px solid #2563eb;
        margin: 15px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITLE
# ============================================================

st.markdown(
    '<div class="deluxy-title">💎 DELUXY.Ai</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="deluxy-subtitle">'
    'AI Engineering Assistant for Parametric 3D CAD'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# MATERIAL DATABASE
# ============================================================

MATERIALS = {
    "Steel": {
        "density": 7.85,
        "color": "#64748b"
    },
    "Stainless Steel": {
        "density": 8.00,
        "color": "#cbd5e1"
    },
    "Aluminium": {
        "density": 2.70,
        "color": "#e2e8f0"
    },
    "Brass": {
        "density": 8.40,
        "color": "#eab308"
    },
    "Copper": {
        "density": 8.96,
        "color": "#b45309"
    },
    "Titanium": {
        "density": 4.50,
        "color": "#94a3b8"
    },
    "Plastic": {
        "density": 1.05,
        "color": "#38bdf8"
    }
}


# ============================================================
# SESSION STATE
# ============================================================

if "cad_state" not in st.session_state:
    st.session_state.cad_state = {
        "component_type": "gear",
        "material": "Steel",
        "units": "mm",
        "parameters": {
            "teeth": 24,
            "module": 2.0,
            "pressure_angle": 20.0,
            "thickness": 8.0,
            "bore_diameter": 10.0
        },
        "answer": "",
        "engineering_notes": []
    }


if "cad_shape" not in st.session_state:
    st.session_state.cad_shape = None


# ============================================================
# API KEY
# ============================================================

def get_openai_key():
    try:
        key = st.secrets.get("OPENAI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.environ.get("OPENAI_API_KEY")


# ============================================================
# LOCAL COMPONENT CLASSIFIER
# ============================================================

def classify_component(text):
    text = text.lower()

    if any(
        word in text
        for word in [
            "gear",
            "roda gigi",
            "roda-gigi",
            "spur gear",
            "spur",
            "gigi"
        ]
    ):
        return "gear"

    if any(
        word in text
        for word in [
            "stepped shaft",
            "poros bertingkat",
            "poros bertingkat"
        ]
    ):
        return "stepped_shaft"

    if any(
        word in text
        for word in [
            "shaft",
            "poros"
        ]
    ):
        return "shaft"

    if any(
        word in text
        for word in [
            "cylinder",
            "silinder"
        ]
    ):
        return "cylinder"

    return None


# ============================================================
# NUMBER EXTRACTION
# ============================================================

def number_after(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(
                    match.group(1).replace(",", ".")
                )
            except Exception:
                pass

    return None


def integer_after(text, patterns):
    value = number_after(text, patterns)

    if value is None:
        return None

    return int(value)


# ============================================================
# LOCAL PARSER
# ============================================================

def local_parser(prompt, previous_state):
    text = prompt.lower()

    previous_parameters = dict(
        previous_state.get("parameters", {})
    )

    component = classify_component(text)

    if component is None:
        component = previous_state.get(
            "component_type",
            "gear"
        )

    state = {
        "component_type": component,
        "material": previous_state.get(
            "material",
            "Steel"
        ),
        "units": "mm",
        "parameters": previous_parameters,
        "answer": "",
        "engineering_notes": []
    }

    if component == "gear":

        teeth = integer_after(
            text,
            [
                r"(?:jumlah\s*)?(?:gigi|teeth)\s*(?:=|:|sebanyak)?\s*(\d+)",
                r"(\d+)\s*(?:gigi|teeth)"
            ]
        )

        module = number_after(
            text,
            [
                r"(?:module|modul)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        bore = number_after(
            text,
            [
                r"(?:bore|lubang tengah|diameter lubang|lubang)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)",
                r"(?:bore|lubang)\s*(?:diameter)?\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        thickness = number_after(
            text,
            [
                r"(?:tebal|thickness)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        pressure_angle = number_after(
            text,
            [
                r"(?:pressure angle|sudut tekanan)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        if teeth is not None:
            state["parameters"]["teeth"] = teeth

        if module is not None:
            state["parameters"]["module"] = module

        if bore is not None:
            state["parameters"]["bore_diameter"] = bore

        if thickness is not None:
            state["parameters"]["thickness"] = thickness

        if pressure_angle is not None:
            state["parameters"]["pressure_angle"] = pressure_angle

        state["parameters"].setdefault(
            "teeth",
            24
        )

        state["parameters"].setdefault(
            "module",
            2.0
        )

        state["parameters"].setdefault(
            "pressure_angle",
            20.0
        )

        state["parameters"].setdefault(
            "thickness",
            8.0
        )

        state["parameters"].setdefault(
            "bore_diameter",
            10.0
        )

        state["answer"] = (
            f"Saya mendeteksi spur gear dengan "
            f"{state['parameters']['teeth']} gigi, "
            f"module {state['parameters']['module']} mm, "
            f"tebal {state['parameters']['thickness']} mm, "
            f"dan bore {state['parameters']['bore_diameter']} mm."
        )

    elif component == "shaft":

        diameter = number_after(
            text,
            [
                r"(?:diameter|diam)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        length = number_after(
            text,
            [
                r"(?:panjang|length)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        bore = number_after(
            text,
            [
                r"(?:bore|lubang)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        if diameter is not None:
            state["parameters"]["diameter"] = diameter

        if length is not None:
            state["parameters"]["length"] = length

        if bore is not None:
            state["parameters"]["bore_diameter"] = bore

        state["parameters"].setdefault(
            "diameter",
            20.0
        )

        state["parameters"].setdefault(
            "length",
            100.0
        )

        state["parameters"].setdefault(
            "bore_diameter",
            0.0
        )

        state["answer"] = (
            f"Saya mendeteksi shaft "
            f"diameter {state['parameters']['diameter']} mm "
            f"dan panjang {state['parameters']['length']} mm."
        )

    elif component == "cylinder":

        diameter = number_after(
            text,
            [
                r"(?:diameter|diam)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        length = number_after(
            text,
            [
                r"(?:panjang|length|tinggi)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        bore = number_after(
            text,
            [
                r"(?:bore|lubang)\s*(?:=|:)?\s*(\d+(?:[.,]\d+)?)"
            ]
        )

        if diameter is not None:
            state["parameters"]["diameter"] = diameter

        if length is not None:
            state["parameters"]["length"] = length

        if bore is not None:
            state["parameters"]["bore_diameter"] = bore

        state["parameters"].setdefault(
            "diameter",
            30.0
        )

        state["parameters"].setdefault(
            "length",
            50.0
        )

        state["parameters"].setdefault(
            "bore_diameter",
            0.0
        )

        state["answer"] = (
            f"Saya mendeteksi cylinder "
            f"diameter {state['parameters']['diameter']} mm "
            f"dan panjang {state['parameters']['length']} mm."
        )

    else:
        state["parameters"].setdefault(
            "length",
            100.0
        )

        state["parameters"].setdefault(
            "diameter",
            20.0
        )

        state["answer"] = (
            "Saya mendeteksi poros bertingkat."
        )

    return state


# ============================================================
# OPENAI PARSER
# ============================================================

def openai_parser(prompt, previous_state):
    api_key = get_openai_key()

    if not api_key or not OPENAI_AVAILABLE:
        return local_parser(
            prompt,
            previous_state
        ), "Local Engine"

    client = OpenAI(
        api_key=api_key
    )

    forced_component = classify_component(prompt)

    system_prompt = """
You are DELUXY.Ai Engineering CAD Assistant.

Your job is to understand a user's mechanical CAD request and return
ONLY valid JSON.

You do NOT create images.
You do NOT create CAD geometry.
You only determine the component and its engineering parameters.

Allowed component types:
gear
shaft
stepped_shaft
cylinder

If the user explicitly says gear, roda gigi, spur gear, spur, or gigi,
the component MUST be gear.

Never convert a gear into a cylinder.

For gear return:
teeth
module
pressure_angle
thickness
bore_diameter

For shaft return:
diameter
length
bore_diameter

For cylinder return:
diameter
length
bore_diameter

Use millimeters unless the user explicitly specifies another unit.

Return this JSON structure:

{
  "component_type": "gear",
  "parameters": {},
  "material": "Steel",
  "answer": "short Indonesian explanation",
  "engineering_notes": []
}
"""

    user_prompt = (
        "Previous state:\n"
        + json.dumps(
            previous_state,
            ensure_ascii=False
        )
        + "\n\nUser request:\n"
        + prompt
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0
        )

        raw = response.choices[0].message.content.strip()

        raw = re.sub(
            r"^```json\s*",
            "",
            raw,
            flags=re.IGNORECASE
        )

        raw = re.sub(
            r"^```\s*",
            "",
            raw
        )

        raw = re.sub(
            r"\s*```$",
            "",
            raw
        )

        data = json.loads(raw)

        local_state = local_parser(
            prompt,
            previous_state
        )

        result = {
            "component_type": data.get(
                "component_type",
                local_state["component_type"]
            ),
            "material": data.get(
                "material",
                local_state["material"]
            ),
            "units": "mm",
            "parameters": data.get(
                "parameters",
                local_state["parameters"]
            ),
            "answer": data.get(
                "answer",
                local_state["answer"]
            ),
            "engineering_notes": data.get(
                "engineering_notes",
                []
            )
        }

        if forced_component:
            result["component_type"] = forced_component

        if result["component_type"] == "gear":

            defaults = {
                "teeth": 24,
                "module": 2.0,
                "pressure_angle": 20.0,
                "thickness": 8.0,
                "bore_diameter": 10.0
            }

            for key, value in defaults.items():
                result["parameters"].setdefault(
                    key,
                    value
                )

        return result, "OpenAI GPT"

    except Exception:
        return local_state_with_component(
            prompt,
            previous_state,
            forced_component
        ), "Local Fallback"


def local_state_with_component(
    prompt,
    previous_state,
    forced_component
):
    result = local_parser(
        prompt,
        previous_state
    )

    if forced_component:
        result["component_type"] = forced_component

    return result


# ============================================================
# VALIDATION
# ============================================================

def validate_state(state):

    component = state["component_type"]
    params = state["parameters"]

    if component == "gear":

        teeth = int(params["teeth"])
        module = float(params["module"])
        thickness = float(params["thickness"])
        bore = float(params["bore_diameter"])

        if teeth < 6:
            raise ValueError(
                "Gear membutuhkan minimal 6 gigi."
            )

        if module <= 0:
            raise ValueError(
                "Module harus lebih besar dari 0."
            )

        if thickness <= 0:
            raise ValueError(
                "Tebal gear harus lebih besar dari 0."
            )

        pitch_radius = (
            module * teeth / 2
        )

        root_radius = (
            pitch_radius
            - 1.25 * module
        )

        if bore / 2 >= root_radius:
            raise ValueError(
                "Bore terlalu besar untuk gear ini."
            )

    elif component == "shaft":

        if params["diameter"] <= 0:
            raise ValueError(
                "Diameter shaft harus lebih besar dari 0."
            )

        if params["length"] <= 0:
            raise ValueError(
                "Panjang shaft harus lebih besar dari 0."
            )

    elif component == "cylinder":

        if params["diameter"] <= 0:
            raise ValueError(
                "Diameter cylinder harus lebih besar dari 0."
            )

        if params["length"] <= 0:
            raise ValueError(
                "Panjang cylinder harus lebih besar dari 0."
            )


# ============================================================
# GEAR GENERATOR
# ============================================================

def create_gear(
    teeth,
    module,
    pressure_angle,
    thickness,
    bore
):

    teeth = int(teeth)
    module = float(module)
    thickness = float(thickness)
    bore = float(bore)

    pitch_radius = (
        module * teeth / 2.0
    )

    addendum = module

    dedendum = 1.25 * module

    root_radius = (
        pitch_radius - dedendum
    )

    outer_radius = (
        pitch_radius + addendum
    )

    if bore / 2.0 >= root_radius:
        raise ValueError(
            "Bore terlalu besar."
        )

    base = (
        cq.Workplane("XY")
        .circle(root_radius)
        .extrude(thickness)
    )

    angle_step = (
        2.0 * math.pi / teeth
    )

    for tooth_index in range(teeth):

        center = (
            tooth_index * angle_step
        )

        root_left = center - angle_step * 0.48
        root_right = center + angle_step * 0.48

        flank_left = center - angle_step * 0.30
        flank_right = center + angle_step * 0.30

        tip_left = center - angle_step * 0.16
        tip_right = center + angle_step * 0.16

        points = []

        for angle, radius in [
            (root_left, root_radius),
            (flank_left, pitch_radius),
            (tip_left, outer_radius),
            (tip_right, outer_radius),
            (flank_right, pitch_radius),
            (root_right, root_radius)
        ]:

            points.append(
                (
                    radius * math.cos(angle),
                    radius * math.sin(angle)
                )
            )

        tooth = (
            cq.Workplane("XY")
            .polyline(points)
            .close()
            .extrude(thickness)
        )

        base = base.union(tooth)

    bore_tool = (
        cq.Workplane("XY")
        .circle(bore / 2.0)
        .extrude(thickness)
    )

    result = base.cut(
        bore_tool
    )

    return result


# ============================================================
# SHAFT GENERATOR
# ============================================================

def create_shaft(
    diameter,
    length,
    bore_diameter
):

    model = (
        cq.Workplane("XY")
        .circle(diameter / 2.0)
        .extrude(length)
    )

    if bore_diameter > 0:

        bore = (
            cq.Workplane("XY")
            .circle(bore_diameter / 2.0)
            .extrude(length)
        )

        model = model.cut(
            bore
        )

    return model


# ============================================================
# CYLINDER GENERATOR
# ============================================================

def create_cylinder(
    diameter,
    length,
    bore_diameter
):

    model = (
        cq.Workplane("XY")
        .circle(diameter / 2.0)
        .extrude(length)
    )

    if bore_diameter > 0:

        bore = (
            cq.Workplane("XY")
            .circle(bore_diameter / 2.0)
            .extrude(length)
        )

        model = model.cut(
            bore
        )

    return model


# ============================================================
# STEPPED SHAFT
# ============================================================

def create_stepped_shaft(params):

    length = float(
        params.get(
            "length",
            120
        )
    )

    diameter = float(
        params.get(
            "diameter",
            20
        )
    )

    model = (
        cq.Workplane("XY")
        .circle(diameter / 2.0)
        .extrude(length)
    )

    return model


# ============================================================
# CAD FACTORY
# ============================================================

def build_cad(state):

    if not CAD_AVAILABLE:
        raise RuntimeError(
            "CadQuery belum tersedia. "
            "Pastikan requirements.txt sudah benar."
        )

    validate_state(state)

    component = state["component_type"]
    params = state["parameters"]

    if component == "gear":

        return create_gear(
            params["teeth"],
            params["module"],
            params["pressure_angle"],
            params["thickness"],
            params["bore_diameter"]
        )

    if component == "shaft":

        return create_shaft(
            params["diameter"],
            params["length"],
            params.get(
                "bore_diameter",
                0
            )
        )

    if component == "cylinder":

        return create_cylinder(
            params["diameter"],
            params["length"],
            params.get(
                "bore_diameter",
                0
            )
        )

    if component == "stepped_shaft":

        return create_stepped_shaft(
            params
        )

    raise ValueError(
        "Component belum didukung."
    )


# ============================================================
# CAD TO PLOTLY
# ============================================================

def cad_to_plotly(
    shape,
    material
):

    vertices, triangles = (
        shape.val().tessellate(
            0.05,
            0.15
        )
    )

    x = [
        float(v.x)
        for v in vertices
    ]

    y = [
        float(v.y)
        for v in vertices
    ]

    z = [
        float(v.z)
        for v in vertices
    ]

    i = [
        int(t[0])
        for t in triangles
    ]

    j = [
        int(t[1])
        for t in triangles
    ]

    k = [
        int(t[2])
        for t in triangles
    ]

    color = MATERIALS.get(
        material,
        MATERIALS["Steel"]
    )["color"]

    mesh = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=i,
        j=j,
        k=k,
        color=color,
        opacity=1.0,
        flatshading=False,
        lighting=dict(
            ambient=0.3,
            diffuse=0.8,
            specular=0.5,
            roughness=0.25
        ),
        lightposition=dict(
            x=100,
            y=100,
            z=150
        )
    )

    fig = go.Figure(
        data=[mesh]
    )

    fig.update_layout(
        height=650,
        margin=dict(
            l=0,
            r=0,
            t=20,
            b=0
        ),
        paper_bgcolor="#080d1c",
        plot_bgcolor="#080d1c",
        scene=dict(
            bgcolor="#080d1c",
            aspectmode="data",
            xaxis=dict(
                title="X (mm)",
                showbackground=False,
                gridcolor="#334155"
            ),
            yaxis=dict(
                title="Y (mm)",
                showbackground=False,
                gridcolor="#334155"
            ),
            zaxis=dict(
                title="Z (mm)",
                showbackground=False,
                gridcolor="#334155"
            ),
            camera=dict(
                eye=dict(
                    x=1.5,
                    y=1.5,
                    z=1.2
                )
            )
        )
    )

    return fig


# ============================================================
# ENGINEERING INFORMATION
# ============================================================

def gear_information(params, material):

    teeth = int(params["teeth"])
    module = float(params["module"])
    thickness = float(params["thickness"])
    bore = float(params["bore_diameter"])

    pitch_diameter = (
        module * teeth
    )

    outside_diameter = (
        pitch_diameter + 2 * module
    )

    root_diameter = (
        pitch_diameter - 2.5 * module
    )

    outer_area = (
        math.pi
        * (outside_diameter / 2) ** 2
    )

    bore_area = (
        math.pi
        * (bore / 2) ** 2
    )

    approximate_volume = (
        max(
            outer_area - bore_area,
            0
        )
        * thickness
    )

    density = MATERIALS[
        material
    ]["density"]

    mass_grams = (
        approximate_volume
        * density
        / 1000
    )

    return {
        "Teeth": teeth,
        "Module": module,
        "Pitch Diameter": pitch_diameter,
        "Outside Diameter": outside_diameter,
        "Root Diameter": root_diameter,
        "Pressure Angle": params.get(
            "pressure_angle",
            20
        ),
        "Thickness": thickness,
        "Bore": bore,
        "Approx. Volume": round(
            approximate_volume,
            2
        ),
        "Approx. Mass (g)": round(
            mass_grams,
            2
        )
    }


# ============================================================
# EXPORT
# ============================================================

def export_step(shape):

    path = (
        "/tmp/deluxy_model.step"
    )

    cq.exporters.export(
        shape,
        path,
        exportType="STEP"
    )

    return Path(
        path
    ).read_bytes()


def export_stl(shape):

    path = (
        "/tmp/deluxy_model.stl"
    )

    cq.exporters.export(
        shape,
        path,
        exportType="STL",
        tolerance=0.01,
        angularTolerance=0.1
    )

    return Path(
        path
    ).read_bytes()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ DELUXY Engine"
    )

    if CAD_AVAILABLE:
        st.success(
            "CAD Engine: READY"
        )
    else:
        st.error(
            "CAD Engine: NOT READY"
        )

    if get_openai_key() and OPENAI_AVAILABLE:
        st.success(
            "OpenAI: CONNECTED"
        )
    else:
        st.warning(
            "OpenAI: LOCAL MODE"
        )

    st.divider()

    current_material = st.session_state.cad_state.get(
        "material",
        "Steel"
    )

    material = st.selectbox(
        "Material",
        list(MATERIALS.keys()),
        index=list(
            MATERIALS.keys()
        ).index(
            current_material
        )
    )

    st.session_state.cad_state[
        "material"
    ] = material


# ============================================================
# CHAT INPUT
# ============================================================

st.subheader(
    "🧠 Apa yang ingin Anda buat?"
)

prompt = st.text_area(
    "Instruksi CAD",
    height=120,
    placeholder=(
        "Contoh: Buat gear 24 gigi, "
        "module 2, tebal 8mm, bore 10mm"
    ),
    label_visibility="collapsed"
)


col1, col2 = st.columns(2)

with col1:

    generate = st.button(
        "🚀 GENERATE CAD",
        type="primary",
        use_container_width=True
    )

with col2:

    reset = st.button(
        "↩️ RESET",
        use_container_width=True
    )


# ============================================================
# RESET
# ============================================================

if reset:

    st.session_state.cad_state = {
        "component_type": "gear",
        "material": "Steel",
        "units": "mm",
        "parameters": {
            "teeth": 24,
            "module": 2.0,
            "pressure_angle": 20.0,
            "thickness": 8.0,
            "bore_diameter": 10.0
        },
        "answer": "",
        "engineering_notes": []
    }

    st.session_state.cad_shape = None

    st.rerun()


# ============================================================
# GENERATE
# ============================================================

if generate:

    if not prompt.strip():

        st.warning(
            "Masukkan instruksi terlebih dahulu."
        )

    else:

        previous_state = (
            st.session_state.cad_state
        )

        with st.spinner(
            "DELUXY.Ai sedang membaca permintaan..."
        ):

            state, engine = (
                openai_parser(
                    prompt.strip(),
                    previous_state
                )
            )

        state["material"] = material

        st.session_state.cad_state = state

        try:

            with st.spinner(
                "Membangun solid CAD..."
            ):

                shape = build_cad(
                    state
                )

            st.session_state.cad_shape = shape

            st.success(
                f"CAD berhasil dibuat menggunakan {engine}."
            )

        except Exception as error:

            st.session_state.cad_shape = None

            st.error(
                f"CAD gagal dibuat: {error}"
            )


# ============================================================
# AI RESPONSE
# ============================================================

state = st.session_state.cad_state

if state.get("answer"):

    st.markdown(
        f"""
        <div class="ai-card">
        <b>🤖 DELUXY.Ai</b><br><br>
        {state["answer"]}
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PARAMETERS
# ============================================================

st.subheader(
    "📐 Engineering Parameters"
)

component = state["component_type"]
params = state["parameters"]

if component == "gear":

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        params["teeth"] = st.number_input(
            "Jumlah Gigi",
            min_value=6,
            value=int(
                params.get(
                    "teeth",
                    24
                )
            ),
            step=1
        )

    with c2:
        params["module"] = st.number_input(
            "Module",
            min_value=0.1,
            value=float(
                params.get(
                    "module",
                    2
                )
            ),
            step=0.1
        )

    with c3:
        params["pressure_angle"] = st.number_input(
            "Pressure Angle",
            min_value=5.0,
            max_value=45.0,
            value=float(
                params.get(
                    "pressure_angle",
                    20
                )
            ),
            step=1.0
        )

    with c4:
        params["thickness"] = st.number_input(
            "Thickness",
            min_value=0.1,
            value=float(
                params.get(
                    "thickness",
                    8
                )
            ),
            step=0.5
        )

    with c5:
        params["bore_diameter"] = st.number_input(
            "Bore",
            min_value=0.1,
            value=float(
                params.get(
                    "bore_diameter",
                    10
                )
            ),
            step=0.5
        )

else:

    c1, c2, c3 = st.columns(3)

    with c1:
        params["diameter"] = st.number_input(
            "Diameter",
            min_value=0.1,
            value=float(
                params.get(
                    "diameter",
                    20
                )
            ),
            step=1.0
        )

    with c2:
        params["length"] = st.number_input(
            "Length",
            min_value=0.1,
            value=float(
                params.get(
                    "length",
                    100
                )
            ),
            step=1.0
        )

    with c3:
        params["bore_diameter"] = st.number_input(
            "Bore",
            min_value=0.0,
            value=float(
                params.get(
                    "bore_diameter",
                    0
                )
            ),
            step=1.0
        )


# ============================================================
# REBUILD
# ============================================================

if st.button(
    "🔧 REBUILD MODEL",
    use_container_width=True
):

    try:

        with st.spinner(
            "Rebuilding CAD..."
        ):

            st.session_state.cad_shape = (
                build_cad(
                    st.session_state.cad_state
                )
            )

        st.success(
            "Model berhasil di-rebuild."
        )

    except Exception as error:

        st.error(
            f"Rebuild gagal: {error}"
        )


# ============================================================
# MODEL
# ============================================================

shape = st.session_state.cad_shape

if shape is not None:

    st.subheader(
        "🧊 3D CAD Preview"
    )

    try:

        fig = cad_to_plotly(
            shape,
            state["material"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "scrollZoom": True
            }
        )

    except Exception as error:

        st.error(
            f"3D viewer gagal: {error}"
        )


    # ========================================================
    # ENGINEERING INFO
    # ========================================================

    if component == "gear":

        st.subheader(
            "📊 Engineering Information"
        )

        info = gear_information(
            params,
            state["material"]
        )

        info_cols = st.columns(
            4
        )

        items = list(
            info.items()
        )

        for index, (key, value) in enumerate(items):

            with info_cols[
                index % 4
            ]:

                st.metric(
                    key,
                    value
                )


    # ========================================================
    # EXPORT
    # ========================================================

    st.subheader(
        "📦 Export CAD"
    )

    e1, e2 = st.columns(2)

    with e1:

        try:

            st.download_button(
                "⬇️ DOWNLOAD STEP",
                data=export_step(
                    shape
                ),
                file_name="DELUXY_model.step",
                mime="application/step",
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"STEP export error: {error}"
            )

    with e2:

        try:

            st.download_button(
                "⬇️ DOWNLOAD STL",
                data=export_stl(
                    shape
                ),
                file_name="DELUXY_model.stl",
                mime="model/stl",
                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"STL export error: {error}"
            )

else:

    st.info(
        "Masukkan spesifikasi komponen lalu klik GENERATE CAD."
    )


# ============================================================
# DIAGNOSTICS
# ============================================================

with st.expander(
    "🔍 Diagnostics"
):

    st.json(
        {
            "CAD Engine": CAD_AVAILABLE,
            "OpenAI SDK": OPENAI_AVAILABLE,
            "OpenAI Key": bool(
                get_openai_key()
            ),
            "Component": state[
                "component_type"
            ],
            "Material": state[
                "material"
            ],
            "Parameters": state[
                "parameters"
            ]
        }
    )
