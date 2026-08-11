import streamlit as st
import os
import re
import json
import math
from pathlib import Path

# ============================================================
# DELUXY.Ai — PARAMETRIC CAD ENGINE V2
# ============================================================

st.set_page_config(
    page_title="DELUXY.Ai CAD",
    page_icon="💎",
    layout="wide"
)

# ============================================================
# IMPORT ENGINES
# ============================================================

try:
    import cadquery as cq
    CAD_OK = True
except Exception:
    cq = None
    CAD_OK = False

try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except Exception:
    go = None
    PLOTLY_OK = False

try:
    import google.generativeai as genai
    GEMINI_OK = True
except Exception:
    genai = None
    GEMINI_OK = False


# ============================================================
# UI STYLE
# ============================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.3rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 22px;
    border-radius: 18px;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    border: 1px solid #334155;
    margin-bottom: 20px;
}

.hero h1 {
    margin: 0;
    color: #f8fafc;
    font-size: 2.2rem;
}

.hero p {
    color: #94a3b8;
    margin-top: 8px;
}

.status {
    padding: 10px 14px;
    border-radius: 10px;
    background: #111827;
    border: 1px solid #334155;
}

</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">

<h1>💎 DELUXY.Ai — Parametric CAD Engine V2</h1>

<p>
Natural Language → Engineering Parameters → OpenCascade Solid → Interactive 3D CAD
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# DEFAULT STATE
# ============================================================

DEFAULT_STATE = {
    "component_type": "gear",
    "material": "Steel",
    "units": "mm",

    "parameters": {

        "teeth": 24,

        "module": 2.0,

        "pressure_angle": 20.0,

        "thickness": 8.0,

        "bore_diameter": 10.0
    }
}


if "cad_state" not in st.session_state:

    st.session_state.cad_state = DEFAULT_STATE.copy()


if "shape" not in st.session_state:

    st.session_state.shape = None


# ============================================================
# MATERIAL DATABASE
# ============================================================

MATERIALS = {

    "Steel": 7.85,

    "Stainless Steel": 8.00,

    "Aluminium": 2.70,

    "Brass": 8.40,

    "Copper": 8.96,

    "Titanium": 4.50,

    "Plastic": 1.05

}


# ============================================================
# TEXT PARSER HELPERS
# ============================================================

def extract_number(text, pattern):

    match = re.search(pattern, text.lower())

    if not match:
        return None

    return float(
        match.group(1).replace(",", ".")
    )


def extract_integer(text, pattern):

    match = re.search(pattern, text.lower())

    if not match:
        return None

    return int(match.group(1))


# ============================================================
# COMPONENT DETECTION
# ============================================================

def detect_component(text):

    text = text.lower()

    if any(
        x in text
        for x in [
            "gear",
            "roda gigi",
            "spur gear",
            "spur"
        ]
    ):

        return "gear"

    if any(
        x in text
        for x in [
            "stepped shaft",
            "poros bertingkat"
        ]
    ):

        return "stepped_shaft"

    if (
        "shaft" in text
        or
        "poros" in text
    ):

        return "shaft"

    if (
        "cylinder" in text
        or
        "silinder" in text
    ):

        return "cylinder"

    return None


# ============================================================
# LOCAL ENGINEERING PARSER
# ============================================================

def local_parse(prompt, old_state):

    text = prompt.lower()

    state = {

        "component_type":
            detect_component(text)
            or old_state["component_type"],

        "material":
            old_state.get(
                "material",
                "Steel"
            ),

        "units":
            "mm",

        "parameters":
            dict(
                old_state["parameters"]
            )
    }


    # --------------------------------------------------------
    # MATERIAL
    # --------------------------------------------------------

    for material in MATERIALS:

        if material.lower() in text:

            state["material"] = material


    # ========================================================
    # GEAR
    # ========================================================

    if state["component_type"] == "gear":

        teeth = extract_integer(
            text,
            r"(?:jumlah\s*)?"
            r"(?:gigi|teeth)"
            r"\s*(?:=|:|sebanyak)?"
            r"\s*(\d+)"
        )

        module = extract_number(
            text,
            r"(?:module|modul)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        pitch = extract_number(
            text,
            r"(?:pitch\s*diameter|diameter\s*pitch)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        bore = extract_number(
            text,
            r"(?:bore|lubang(?:\s+tengah)?|diameter\s*lubang)"
            r"\s*(?:=|:|diameter)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        thickness = extract_number(
            text,
            r"(?:tebal|thickness)"
            r"\s*(?:=|:|nya)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        pressure_angle = extract_number(
            text,
            r"(?:pressure\s*angle|sudut\s*tekanan)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )


        if teeth is not None:

            state["parameters"]["teeth"] = teeth


        if module is not None:

            state["parameters"]["module"] = module

        elif pitch is not None and teeth:

            state["parameters"]["module"] = (
                pitch / teeth
            )


        if bore is not None:

            state["parameters"]["bore_diameter"] = bore


        if thickness is not None:

            state["parameters"]["thickness"] = thickness


        if pressure_angle is not None:

            state["parameters"]["pressure_angle"] = pressure_angle


    # ========================================================
    # SHAFT
    # ========================================================

    elif state["component_type"] in (
        "shaft",
        "stepped_shaft"
    ):

        length = extract_number(
            text,
            r"(?:panjang|length)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        diameter = extract_number(
            text,
            r"(?:diameter utama|diameter|diam)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        bore = extract_number(
            text,
            r"(?:bore|lubang)"
            r"\s*(?:=|:|tengah)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )


        if length is not None:

            state["parameters"]["length"] = length


        if diameter is not None:

            state["parameters"]["diameter"] = diameter


        if bore is not None:

            state["parameters"]["bore_diameter"] = bore


    # ========================================================
    # CYLINDER
    # ========================================================

    elif state["component_type"] == "cylinder":

        diameter = extract_number(
            text,
            r"(?:diameter|diam)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        length = extract_number(
            text,
            r"(?:panjang|length|tinggi)"
            r"\s*(?:=|:)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )

        bore = extract_number(
            text,
            r"(?:bore|lubang)"
            r"\s*(?:=|:|tengah)?"
            r"\s*(\d+(?:[.,]\d+)?)"
        )


        if diameter is not None:

            state["parameters"]["diameter"] = diameter


        if length is not None:

            state["parameters"]["length"] = length


        if bore is not None:

            state["parameters"]["bore_diameter"] = bore


    return state


# ============================================================
# GEMINI PARSER
# ============================================================

def parse_with_gemini(prompt, old_state):

    api_key = None

    try:

        api_key = st.secrets.get(
            "GEMINI_API_KEY"
        )

    except Exception:

        pass


    if not api_key:

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )


    # Fallback kalau API key tidak tersedia

    if not api_key or not GEMINI_OK:

        return (
            local_parse(
                prompt,
                old_state
            ),
            "Local Parser"
        )


    instruction = """
You are DELUXY.Ai mechanical engineering CAD parser.

Return ONLY valid JSON.

Allowed component_type:

gear
shaft
stepped_shaft
cylinder

For gear use:

teeth
module
pressure_angle
thickness
bore_diameter

For shaft use:

length
diameter
bore_diameter

For cylinder use:

diameter
length
bore_diameter

Default gear pressure_angle = 20.

Preserve previous values if user does not specify a value.

Never invent a different component.
"""


    try:

        genai.configure(
            api_key=api_key
        )


        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )


        response = model.generate_content(

            instruction

            + "\n\nPREVIOUS STATE:\n"

            + json.dumps(
                old_state
            )

            + "\n\nUSER REQUEST:\n"

            + prompt
        )


        raw = response.text.strip()


        raw = re.sub(
            r"^```json\s*",
            "",
            raw
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


        state = {

            "component_type":
                data.get(
                    "component_type",
                    old_state["component_type"]
                ),

            "material":
                data.get(
                    "material",
                    old_state.get(
                        "material",
                        "Steel"
                    )
                ),

            "units":
                "mm",

            "parameters":
                data.get(
                    "parameters",
                    old_state["parameters"]
                )
        }


        return state, "Gemini"


    except Exception:

        return (
            local_parse(
                prompt,
                old_state
            ),
            "Local Fallback"
        )


# ============================================================
# REAL GEAR CAD
# ============================================================

def make_spur_gear(
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


    if teeth < 6:

        raise ValueError(
            "Jumlah gigi minimal 6."
        )


    if module <= 0:

        raise ValueError(
            "Module harus lebih besar dari 0."
        )


    if thickness <= 0:

        raise ValueError(
            "Tebal gear harus lebih besar dari 0."
        )


    if bore <= 0:

        raise ValueError(
            "Bore harus lebih besar dari 0."
        )


    # ========================================================
    # BASIC GEAR CALCULATIONS
    # ========================================================

    pitch_radius = (
        module * teeth / 2
    )


    addendum = module

    dedendum = 1.25 * module


    outer_radius = (
        pitch_radius
        + addendum
    )


    root_radius = (
        pitch_radius
        - dedendum
    )


    bore_radius = bore / 2


    if bore_radius >= root_radius:

        raise ValueError(
            "Bore terlalu besar "
            "untuk diameter root gear."
        )


    # ========================================================
    # TOOTH GEOMETRY
    # ========================================================

    angular_pitch = (
        2 * math.pi / teeth
    )


    tooth_half_angle = (
        angular_pitch * 0.24
    )


    flank_radius = max(
        root_radius,
        pitch_radius - module * 0.25
    )


    # ========================================================
    # ROOT DISC
    # ========================================================

    result = (

        cq.Workplane("XY")

        .circle(root_radius)

        .extrude(thickness)
    )


    # ========================================================
    # BUILD EACH TOOTH
    # ========================================================

    for tooth_number in range(teeth):

        center_angle = (
            tooth_number
            * angular_pitch
        )


        tooth_profile = [

            (
                -angular_pitch * 0.50,
                root_radius
            ),

            (
                -tooth_half_angle,
                flank_radius
            ),

            (
                -tooth_half_angle * 0.55,
                outer_radius
            ),

            (
                tooth_half_angle * 0.55,
                outer_radius
            ),

            (
                tooth_half_angle,
                flank_radius
            ),

            (
                angular_pitch * 0.50,
                root_radius
            )
        ]


        points = []


        for delta_angle, radius in tooth_profile:

            angle = (
                center_angle
                + delta_angle
            )


            x = (
                radius
                * math.cos(angle)
            )


            y = (
                radius
                * math.sin(angle)
            )


            points.append(
                (x, y)
            )


        tooth = (

            cq.Workplane("XY")

            .polyline(points)

            .close()

            .extrude(thickness)
        )


        result = result.union(
            tooth
        )


    # ========================================================
    # CENTER BORE
    # ========================================================

    bore_tool = (

        cq.Workplane("XY")

        .circle(bore_radius)

        .extrude(thickness)
    )


    result = result.cut(
        bore_tool
    )


    return result


# ============================================================
# GENERIC CAD GENERATOR
# ============================================================

def make_cad(state):

    if not CAD_OK:

        raise RuntimeError(
            "CadQuery belum ter-install. "
            "Pastikan requirements.txt sudah "
            "berisi cadquery kemudian redeploy."
        )


    component = (
        state["component_type"]
    )


    params = (
        state["parameters"]
    )


    # ========================================================
    # GEAR
    # ========================================================

    if component == "gear":

        return make_spur_gear(

            params["teeth"],

            params["module"],

            params.get(
                "pressure_angle",
                20
            ),

            params["thickness"],

            params["bore_diameter"]
        )


    # ========================================================
    # SHAFT
    # ========================================================

    if component == "shaft":

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


        bore = float(
            params.get(
                "bore_diameter",
                0
            )
        )


        model = (

            cq.Workplane("XY")

            .circle(
                diameter / 2
            )

            .extrude(
                length
            )
        )


        if bore > 0:

            model = model.cut(

                cq.Workplane("XY")

                .circle(
                    bore / 2
                )

                .extrude(
                    length
                )
            )


        return model


    # ========================================================
    # CYLINDER
    # ========================================================

    if component == "cylinder":

        diameter = float(
            params.get(
                "diameter",
                30
            )
        )


        length = float(
            params.get(
                "length",
                50
            )
        )


        bore = float(
            params.get(
                "bore_diameter",
                0
            )
        )


        model = (

            cq.Workplane("XY")

            .circle(
                diameter / 2
            )

            .extrude(
                length
            )
        )


        if bore > 0:

            model = model.cut(

                cq.Workplane("XY")

                .circle(
                    bore / 2
                )

                .extrude(
                    length
                )
            )


        return model


    # ========================================================
    # STEPPED SHAFT FALLBACK
    # ========================================================

    if component == "stepped_shaft":

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


        return (

            cq.Workplane("XY")

            .circle(
                diameter / 2
            )

            .extrude(
                length
            )
        )


    raise ValueError(
        "Jenis komponen belum didukung."
    )


# ============================================================
# 3D VIEWER
# ============================================================

def show_3d(
    shape,
    title
):

    if not PLOTLY_OK:

        st.error(
            "Plotly belum ter-install."
        )

        return


    # OpenCascade tessellation

    vertices, triangles = (
        shape.val().tessellate(
            0.03,
            0.10
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


    mesh = go.Mesh3d(

        x=x,

        y=y,

        z=z,

        i=i,

        j=j,

        k=k,

        color="#3b82f6",

        opacity=1.0,

        flatshading=False,

        lighting=dict(

            ambient=0.25,

            diffuse=0.85,

            specular=0.70,

            roughness=0.20,

            fresnel=0.12
        ),

        lightposition=dict(

            x=100,

            y=100,

            z=180
        ),

        hoverinfo="skip"
    )


    fig = go.Figure(
        data=[mesh]
    )


    fig.update_layout(

        title=title,

        height=700,

        margin=dict(
            l=0,
            r=0,
            t=45,
            b=0
        ),

        paper_bgcolor="#0b1020",

        scene=dict(

            bgcolor="#0b1020",

            aspectmode="data",

            camera=dict(

                eye=dict(

                    x=1.5,

                    y=1.5,

                    z=1.15
                )
            ),

            xaxis=dict(
                title="X (mm)",
                gridcolor="#334155"
            ),

            yaxis=dict(
                title="Y (mm)",
                gridcolor="#334155"
            ),

            zaxis=dict(
                title="Z (mm)",
                gridcolor="#334155"
            )
        )
    )


    st.plotly_chart(

        fig,

        use_container_width=True,

        config={

            "displaylogo": False,

            "scrollZoom": True,

            "toImageButtonOptions": {

                "format": "png",

                "filename":
                    "DELUXY_CAD",

                "scale": 2
            }
        }
    )


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

        angularTolerance=0.10
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


    if CAD_OK:

        st.success(
            "OpenCascade / CadQuery: READY"
        )

    else:

        st.error(
            "OpenCascade / CadQuery: NOT INSTALLED"
        )


    if GEMINI_OK:

        st.success(
            "Gemini SDK: READY"
        )

    else:

        st.warning(
            "Gemini SDK: unavailable"
        )


    current_material = (
        st.session_state
        .cad_state
        .get(
            "material",
            "Steel"
        )
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


# ============================================================
# USER PROMPT
# ============================================================

prompt = st.text_area(

    "🧠 Jelaskan komponen yang ingin dibuat",

    height=120,

    placeholder="""
Contoh:

Buat gear 24 gigi, module 2,
tebal 8mm, bore 10mm

atau:

Buat shaft diameter 20mm
panjang 120mm bore 8mm
"""
)


button1, button2 = st.columns(2)


with button1:

    generate = st.button(

        "🚀 GENERATE CAD",

        type="primary",

        use_container_width=True
    )


with button2:

    reset = st.button(

        "↩️ RESET",

        use_container_width=True
    )


# ============================================================
# RESET
# ============================================================

if reset:

    st.session_state.cad_state = (
        DEFAULT_STATE.copy()
    )

    st.session_state.shape = None

    st.rerun()


# ============================================================
# GENERATE
# ============================================================

if generate and prompt.strip():

    with st.spinner(
        "AI membaca spesifikasi engineering..."
    ):

        state, parser = (
            parse_with_gemini(

                prompt.strip(),

                st.session_state.cad_state
            )
        )


    state["material"] = material


    st.session_state.cad_state = (
        state
    )


    try:

        with st.spinner(
            "OpenCascade membangun solid CAD..."
        ):

            st.session_state.shape = (
                make_cad(state)
            )


        st.success(
            f"Model berhasil dibuat • Parser: {parser}"
        )


    except Exception as error:

        st.session_state.shape = None

        st.error(
            f"CAD generation gagal: {error}"
        )


# ============================================================
# PARAMETER EDITOR
# ============================================================

state = (
    st.session_state.cad_state
)


params = (
    state["parameters"]
)


st.subheader(
    "📐 Engineering Parameters"
)


if state["component_type"] == "gear":

    fields = [

        (
            "Jumlah Gigi",
            "teeth",
            1
        ),

        (
            "Module (mm)",
            "module",
            0.1
        ),

        (
            "Pressure Angle (°)",
            "pressure_angle",
            1
        ),

        (
            "Tebal (mm)",
            "thickness",
            0.1
        ),

        (
            "Bore (mm)",
            "bore_diameter",
            0.1
        )
    ]

else:

    fields = [

        (
            key.replace(
                "_",
                " "
            ).title(),

            key,

            0.1
        )

        for key
        in list(params.keys())[:5]
    ]


columns = st.columns(
    len(fields)
)


for column, field in zip(
    columns,
    fields
):

    label, key, step = field


    with column:

        old_value = params.get(
            key,
            0
        )


        if key == "teeth":

            params[key] = int(

                st.number_input(

                    label,

                    value=int(
                        old_value
                    ),

                    step=1
                )
            )

        else:

            params[key] = float(

                st.number_input(

                    label,

                    value=float(
                        old_value
                    ),

                    step=step
                )
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

            st.session_state.shape = (
                make_cad(state)
            )


        st.success(
            "Model berhasil diperbarui."
        )


    except Exception as error:

        st.error(
            f"Rebuild gagal: {error}"
        )


# ============================================================
# 3D MODEL
# ============================================================

shape = (
    st.session_state.shape
)


if shape is not None:

    st.subheader(
        "🧊 Real 3D CAD Preview"
    )


    show_3d(

        shape,

        (
            state["component_type"]
            .replace(
                "_",
                " "
            )
            .title()
            +
            " • "
            +
            state["material"]
        )
    )


    st.subheader(
        "📦 Export CAD"
    )


    export1, export2 = (
        st.columns(2)
    )


    with export1:

        try:

            st.download_button(

                "⬇️ DOWNLOAD STEP",

                data=export_step(
                    shape
                ),

                file_name=(
                    "DELUXY_model.step"
                ),

                mime=(
                    "application/step"
                ),

                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"STEP export gagal: {error}"
            )


    with export2:

        try:

            st.download_button(

                "⬇️ DOWNLOAD STL",

                data=export_stl(
                    shape
                ),

                file_name=(
                    "DELUXY_model.stl"
                ),

                mime="model/stl",

                use_container_width=True
            )

        except Exception as error:

            st.error(
                f"STL export gagal: {error}"
            )


else:

    st.info(
        "Masukkan spesifikasi lalu klik GENERATE CAD."
    )


# ============================================================
# DIAGNOSTICS
# ============================================================

with st.expander(
    "🔍 Engine Diagnostics"
):

    st.json({

        "CadQuery":
            CAD_OK,

        "OpenCascade":
            CAD_OK,

        "Plotly":
            PLOTLY_OK,

        "Gemini":
            GEMINI_OK,

        "Component":
            state["component_type"],

        "Material":
            state["material"],

        "Parameters":
            state["parameters"]
    })
