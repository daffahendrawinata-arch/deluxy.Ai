import streamlit as st
import math
import os
import tempfile
import json
import re
import io

# ============================================================
# DELUXY.Ai CAD ENGINE V2
# Parametric Engineering CAD Generator
#
# Features:
# - AI / local natural language parser
# - Involute spur gear
# - Stepped shaft
# - Cylinder
# - High quality CadQuery tessellation preview
# - Engineering calculations
# - 2D engineering view
# - STEP export
# - STL export
# - DXF export
# - JSON engineering report
# ============================================================

st.set_page_config(
    page_title="DELUXY.Ai CAD Engine",
    page_icon="💎",
    layout="wide"
)

# ============================================================
# OPTIONAL IMPORTS
# ============================================================

try:
    import cadquery as cq
    CAD_READY = True
    CAD_ERROR = ""
except Exception as e:
    CAD_READY = False
    CAD_ERROR = str(e)

try:
    import plotly.graph_objects as go
    PLOTLY_READY = True
except Exception:
    PLOTLY_READY = False

try:
    from openai import OpenAI
    OPENAI_READY = True
except Exception:
    OPENAI_READY = False


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 3rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0;
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 1.05rem;
    margin-bottom: 25px;
}

.status-good {
    padding: 14px;
    border-radius: 12px;
    background: #dcfce7;
    color: #166534;
    font-weight: 700;
}

.status-bad {
    padding: 14px;
    border-radius: 12px;
    background: #fee2e2;
    color: #991b1b;
    font-weight: 700;
}

.metric-card {
    padding: 15px;
    border-radius: 12px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💎 DELUXY.Ai</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Parametric AI-Assisted Engineering CAD Generator'
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
        "color": "#d1d5db"
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
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ DELUXY Engine")

    if CAD_READY:

        st.markdown(
            '<div class="status-good">'
            '🟢 CAD Engine: READY'
            '</div>',
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            '<div class="status-bad">'
            '🔴 CAD Engine: NOT READY'
            '</div>',
            unsafe_allow_html=True
        )

        st.code(CAD_ERROR)

    if PLOTLY_READY:
        st.success("🟢 3D Renderer: READY")
    else:
        st.error("🔴 Plotly: NOT READY")

    st.divider()

    material = st.selectbox(
        "Material",
        list(MATERIALS.keys())
    )

    st.divider()

    st.caption("DELUXY.Ai")
    st.caption("Parametric Engineering CAD Engine")


# ============================================================
# NATURAL LANGUAGE REQUEST
# ============================================================

st.subheader("🤖 Describe what you want to build")

user_request = st.text_area(
    "",
    placeholder=(
        "Contoh:\n"
        "Buat gear 24 gigi, module 2, "
        "pressure angle 20 derajat, "
        "bore 10 mm dan tebal 8 mm"
    ),
    height=120
)


# ============================================================
# COMPONENT
# ============================================================

component = st.selectbox(
    "Component Type",
    [
        "Gear",
        "Stepped Shaft",
        "Cylinder"
    ]
)


# ============================================================
# PARAMETERS
# ============================================================

st.subheader("📐 Engineering Parameters")


if component == "Gear":

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        teeth = st.number_input(
            "Teeth",
            min_value=4,
            max_value=500,
            value=24,
            step=1
        )

    with c2:

        module = st.number_input(
            "Module",
            min_value=0.1,
            max_value=50.0,
            value=2.0,
            step=0.1
        )

    with c3:

        pressure_angle = st.number_input(
            "Pressure Angle",
            min_value=10.0,
            max_value=45.0,
            value=20.0,
            step=1.0
        )

    with c4:

        thickness = st.number_input(
            "Thickness",
            min_value=0.5,
            max_value=500.0,
            value=8.0,
            step=0.5
        )

    with c5:

        bore = st.number_input(
            "Bore Ø",
            min_value=0.0,
            max_value=500.0,
            value=10.0,
            step=0.5
        )


elif component == "Stepped Shaft":

    c1, c2, c3 = st.columns(3)

    with c1:

        shaft_length = st.number_input(
            "Overall Length",
            min_value=1.0,
            value=120.0,
            step=1.0
        )

    with c2:

        main_diameter = st.number_input(
            "Main Ø",
            min_value=0.5,
            value=25.0,
            step=0.5
        )

    with c3:

        left_diameter = st.number_input(
            "Left Ø",
            min_value=0.5,
            value=18.0,
            step=0.5
        )

    right_diameter = st.number_input(
        "Right Ø",
        min_value=0.5,
        value=20.0,
        step=0.5
    )


else:

    c1, c2 = st.columns(2)

    with c1:

        cylinder_diameter = st.number_input(
            "Diameter",
            min_value=0.5,
            value=30.0,
            step=0.5
        )

    with c2:

        cylinder_height = st.number_input(
            "Height",
            min_value=0.5,
            value=50.0,
            step=0.5
        )


# ============================================================
# INVOLUTE MATH
# ============================================================

def involute_point(rb, t):

    x = rb * (
        math.cos(t)
        + t * math.sin(t)
    )

    y = rb * (
        math.sin(t)
        - t * math.cos(t)
    )

    return x, y


def rotate_point(x, y, angle):

    c = math.cos(angle)
    s = math.sin(angle)

    return (
        x * c - y * s,
        x * s + y * c
    )


# ============================================================
# TRUE-ISH INVOLUTE GEAR PROFILE
# ============================================================

def create_involute_gear_profile(
    teeth,
    module,
    pressure_angle,
    samples=18
):

    teeth = int(teeth)

    m = float(module)

    alpha = math.radians(
        float(pressure_angle)
    )

    pitch_radius = (
        m * teeth / 2.0
    )

    base_radius = (
        pitch_radius *
        math.cos(alpha)
    )

    addendum = m

    dedendum = 1.25 * m

    outer_radius = (
        pitch_radius +
        addendum
    )

    root_radius = (
        pitch_radius -
        dedendum
    )

    if root_radius <= 0:

        raise ValueError(
            "Root radius tidak valid."
        )

    if base_radius >= outer_radius:

        raise ValueError(
            "Base radius tidak valid."
        )

    # --------------------------------------------------------
    # INVOLUTE AT PITCH CIRCLE
    # --------------------------------------------------------

    t_pitch = math.sqrt(
        (
            pitch_radius /
            base_radius
        ) ** 2 - 1
    )

    theta_pitch = (
        t_pitch -
        math.atan(t_pitch)
    )

    half_tooth_angle = (
        math.pi /
        (2.0 * teeth)
    )

    rotation_offset = (
        half_tooth_angle -
        theta_pitch
    )

    # --------------------------------------------------------
    # INVOLUTE AT OUTER CIRCLE
    # --------------------------------------------------------

    t_outer = math.sqrt(
        (
            outer_radius /
            base_radius
        ) ** 2 - 1
    )

    points = []

    pitch = (
        2.0 *
        math.pi /
        teeth
    )

    # Number of root points
    root_samples = 8

    for tooth in range(teeth):

        center = tooth * pitch

        # ----------------------------------------------------
        # LEFT ROOT
        # ----------------------------------------------------

        left_root_angle = (
            center -
            half_tooth_angle
        )

        for i in range(root_samples):

            a = (
                left_root_angle
                + (
                    pitch /
                    teeth *
                    0.05
                )
                * i /
                (root_samples - 1)
            )

            points.append(
                (
                    root_radius *
                    math.cos(a),
                    root_radius *
                    math.sin(a)
                )
            )

        # ----------------------------------------------------
        # LEFT FLANK
        # ----------------------------------------------------

        left_flank = []

        for i in range(samples + 1):

            t = (
                t_outer *
                i /
                samples
            )

            x, y = involute_point(
                base_radius,
                t
            )

            x, y = rotate_point(
                x,
                y,
                rotation_offset
            )

            x = -x
            y = y

            x, y = rotate_point(
                x,
                y,
                center
            )

            left_flank.append(
                (x, y)
            )

        points.extend(
            reversed(left_flank)
        )

        # ----------------------------------------------------
        # RIGHT FLANK
        # ----------------------------------------------------

        right_flank = []

        for i in range(samples + 1):

            t = (
                t_outer *
                i /
                samples
            )

            x, y = involute_point(
                base_radius,
                t
            )

            x, y = rotate_point(
                x,
                y,
                rotation_offset
            )

            x, y = rotate_point(
                x,
                y,
                center
            )

            right_flank.append(
                (x, y)
            )

        points.extend(
            right_flank
        )

    # --------------------------------------------------------
    # CLEAN DUPLICATES
    # --------------------------------------------------------

    cleaned = []

    for p in points:

        if not cleaned:

            cleaned.append(p)

        else:

            dx = (
                p[0] -
                cleaned[-1][0]
            )

            dy = (
                p[1] -
                cleaned[-1][1]
            )

            if math.hypot(
                dx,
                dy
            ) > 1e-7:

                cleaned.append(p)

    return (
        cleaned,
        pitch_radius,
        base_radius,
        root_radius,
        outer_radius
    )


# ============================================================
# BUILD CADQUERY GEAR
# ============================================================

def build_cadquery_gear(
    teeth,
    module,
    pressure_angle,
    thickness,
    bore
):

    (
        points,
        pitch_radius,
        base_radius,
        root_radius,
        outer_radius
    ) = create_involute_gear_profile(
        teeth,
        module,
        pressure_angle
    )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    gear = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(thickness)
    )

    # --------------------------------------------------------
    # BORE
    # --------------------------------------------------------

    if bore > 0:

        bore_radius = (
            bore / 2.0
        )

        if bore_radius >= root_radius:

            raise ValueError(
                "Bore terlalu besar untuk gear."
            )

        cutter = (
            cq.Workplane("XY")
            .workplane(
                offset=-1
            )
            .circle(
                bore_radius
            )
            .extrude(
                thickness + 2
            )
        )

        gear = gear.cut(
            cutter
        )

    try:

        gear = gear.clean()

    except Exception:
        pass

    if gear.val().isNull():

        raise ValueError(
            "Gear menghasilkan solid invalid."
        )

    return gear


# ============================================================
# SHAFT
# ============================================================

def build_cadquery_shaft(
    length,
    main_diameter,
    left_diameter,
    right_diameter
):

    left_length = (
        length * 0.25
    )

    main_length = (
        length * 0.50
    )

    right_length = (
        length * 0.25
    )

    shaft = (
        cq.Workplane("XY")
        .circle(
            left_diameter / 2
        )
        .extrude(
            left_length
        )
    )

    shaft = (
        shaft
        .faces(">Z")
        .workplane()
        .circle(
            main_diameter / 2
        )
        .extrude(
            main_length
        )
    )

    shaft = (
        shaft
        .faces(">Z")
        .workplane()
        .circle(
            right_diameter / 2
        )
        .extrude(
            right_length
        )
    )

    return shaft


# ============================================================
# CYLINDER
# ============================================================

def build_cadquery_cylinder(
    diameter,
    height
):

    return (
        cq.Workplane("XY")
        .circle(
            diameter / 2
        )
        .extrude(
            height
        )
    )


# ============================================================
# HIGH QUALITY CADQUERY MESH
# ============================================================

def cadquery_to_mesh(
    model,
    tolerance=0.03,
    angular_tolerance=0.08
):

    shape = model.val()

    vertices, triangles = (
        shape.tessellate(
            tolerance,
            angular_tolerance
        )
    )

    xyz = []

    for v in vertices:

        xyz.append(
            (
                v.x,
                v.y,
                v.z
            )
        )

    I = []
    J = []
    K = []

    for a, b, c in triangles:

        I.append(a)
        J.append(b)
        K.append(c)

    return xyz, I, J, K


# ============================================================
# 3D PREVIEW
# ============================================================

def show_cadquery_3d(
    model,
    title,
    material_color
):

    if not PLOTLY_READY:

        st.error(
            "Plotly belum tersedia."
        )

        return

    try:

        (
            vertices,
            I,
            J,
            K
        ) = cadquery_to_mesh(
            model,
            tolerance=0.03,
            angular_tolerance=0.08
        )

    except Exception as e:

        st.error(
            f"3D tessellation gagal: {e}"
        )

        return

    x = [
        v[0]
        for v in vertices
    ]

    y = [
        v[1]
        for v in vertices
    ]

    z = [
        v[2]
        for v in vertices
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=I,
            j=J,
            k=K,

            color=material_color,

            opacity=1.0,

            flatshading=False,

            lighting=dict(
                ambient=0.45,
                diffuse=0.85,
                specular=0.75,
                roughness=0.22,
                fresnel=0.15
            ),

            lightposition=dict(
                x=150,
                y=100,
                z=250
            ),

            hoverinfo="skip"
        )
    )

    fig.update_layout(

        title=title,

        height=700,

        margin=dict(
            l=0,
            r=0,
            t=55,
            b=0
        ),

        paper_bgcolor="#0b1020",

        plot_bgcolor="#0b1020",

        scene=dict(

            xaxis=dict(
                visible=False
            ),

            yaxis=dict(
                visible=False
            ),

            zaxis=dict(
                visible=False
            ),

            aspectmode="data",

            camera=dict(
                eye=dict(
                    x=1.45,
                    y=1.45,
                    z=1.1
                )
            )
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True
        }
    )


# ============================================================
# 2D GEAR DRAWING
# ============================================================

def show_gear_2d(
    points,
    bore,
    pitch_radius,
    base_radius,
    root_radius,
    outer_radius
):

    if not PLOTLY_READY:
        return

    x = [
        p[0]
        for p in points
    ]

    y = [
        p[1]
        for p in points
    ]

    # Close profile
    x.append(x[0])
    y.append(y[0])

    fig = go.Figure()

    # Gear profile
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(
                width=2
            ),
            name="Gear Profile"
        )
    )

    # Bore
    if bore > 0:

        bore_r = bore / 2

        bx = []
        by = []

        for i in range(181):

            a = (
                2 *
                math.pi *
                i /
                180
            )

            bx.append(
                bore_r *
                math.cos(a)
            )

            by.append(
                bore_r *
                math.sin(a)
            )

        fig.add_trace(
            go.Scatter(
                x=bx,
                y=by,
                mode="lines",
                line=dict(
                    width=2,
                    dash="dash"
                ),
                name="Bore"
            )
        )

    # Pitch circle
    px = []
    py = []

    for i in range(181):

        a = (
            2 *
            math.pi *
            i /
            180
        )

        px.append(
            pitch_radius *
            math.cos(a)
        )

        py.append(
            pitch_radius *
            math.sin(a)
        )

    fig.add_trace(
        go.Scatter(
            x=px,
            y=py,
            mode="lines",
            line=dict(
                dash="dot"
            ),
            name="Pitch Circle"
        )
    )

    # Outer circle
    ox = []
    oy = []

    for i in range(181):

        a = (
            2 *
            math.pi *
            i /
            180
        )

        ox.append(
            outer_radius *
            math.cos(a)
        )

        oy.append(
            outer_radius *
            math.sin(a)
        )

    fig.add_trace(
        go.Scatter(
            x=ox,
            y=oy,
            mode="lines",
            line=dict(
                dash="dash"
            ),
            name="Outside Diameter"
        )
    )

    fig.update_layout(

        title="2D Engineering Profile",

        height=650,

        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20
        ),

        xaxis=dict(
            title="X (mm)",
            scaleanchor="y",
            scaleratio=1
        ),

        yaxis=dict(
            title="Y (mm)"
        ),

        hovermode="closest",

        legend=dict(
            orientation="h"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ENGINEERING CALCULATIONS
# ============================================================

def gear_engineering_data(
    teeth,
    module,
    pressure_angle,
    thickness,
    bore,
    material,
    model
):

    (
        points,
        pitch_radius,
        base_radius,
        root_radius,
        outer_radius
    ) = create_involute_gear_profile(
        teeth,
        module,
        pressure_angle
    )

    pitch_diameter = (
        pitch_radius * 2
    )

    base_diameter = (
        base_radius * 2
    )

    root_diameter = (
        root_radius * 2
    )

    outer_diameter = (
        outer_radius * 2
    )

    volume_mm3 = (
        model.val().Volume()
    )

    density = MATERIALS[
        material
    ]["density"]

    mass_kg = (
        volume_mm3 *
        density /
        1_000_000
    )

    return {

        "component": "spur_gear",

        "material": material,

        "teeth": teeth,

        "module_mm": module,

        "pressure_angle_deg":
            pressure_angle,

        "thickness_mm":
            thickness,

        "bore_diameter_mm":
            bore,

        "pitch_diameter_mm":
            pitch_diameter,

        "base_diameter_mm":
            base_diameter,

        "root_diameter_mm":
            root_diameter,

        "outside_diameter_mm":
            outer_diameter,

        "volume_mm3":
            volume_mm3,

        "mass_kg":
            mass_kg
    }


# ============================================================
# EXPORT HELPERS
# ============================================================

def export_step(model):

    path = tempfile.mktemp(
        suffix=".step"
    )

    cq.exporters.export(
        model,
        path,
        cq.exporters.ExportTypes.STEP
    )

    with open(
        path,
        "rb"
    ) as f:

        return f.read()


def export_stl(model):

    path = tempfile.mktemp(
        suffix=".stl"
    )

    model.val().exportStl(
        path,
        tolerance=0.005,
        angularTolerance=0.05,
        ascii=False,
        relative=True,
        parallel=True
    )

    with open(
        path,
        "rb"
    ) as f:

        return f.read()


def export_gear_dxf(
    points,
    bore
):

    path = tempfile.mktemp(
        suffix=".dxf"
    )

    profile = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
    )

    if bore > 0:

        profile = (
            profile
            .circle(bore / 2)
        )

    cq.exporters.exportDXF(
        profile,
        path,
        doc_units=4,
        approx="arc",
        tolerance=0.01
    )

    with open(
        path,
        "rb"
    ) as f:

        return f.read()


# ============================================================
# AI PARSER
# ============================================================

def ai_parse_request(text):

    api_key = None

    try:

        api_key = st.secrets.get(
            "OPENAI_API_KEY"
        )

    except Exception:
        pass

    if not api_key:

        api_key = os.environ.get(
            "OPENAI_API_KEY"
        )

    if (
        not api_key
        or not OPENAI_READY
    ):

        return None

    try:

        client = OpenAI(
            api_key=api_key
        )

        system_prompt = """

You are DELUXY.Ai Engineering CAD Parser.

Convert the user's natural language request
into strict JSON.

Allowed component types:

gear
stepped_shaft
cylinder

For gear return:

component_type
teeth
module
pressure_angle
thickness
bore

For stepped_shaft return:

component_type
length
main_diameter
left_diameter
right_diameter

For cylinder return:

component_type
diameter
height

Use millimeters unless another unit
is explicitly provided.

Convert inches to millimeters.

Return JSON ONLY.
No markdown.
No explanation.

"""

        response = (
            client
            .chat
            .completions
            .create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content":
                            system_prompt
                    },
                    {
                        "role": "user",
                        "content":
                            text
                    }
                ]
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        return json.loads(
            content
        )

    except Exception:

        return None


# ============================================================
# LOCAL PARSER
# ============================================================

def local_parse(text):

    t = text.lower()

    result = {}

    # --------------------------------------------------------
    # GEAR
    # --------------------------------------------------------

    if any(
        word in t
        for word in [
            "gear",
            "gir",
            "roda gigi"
        ]
    ):

        result[
            "component_type"
        ] = "gear"

        # Teeth
        match = re.search(
            r"(\d+)\s*(?:gigi|teeth)",
            t
        )

        if match:

            result["teeth"] = int(
                match.group(1)
            )

        # Module
        match = re.search(
            r"module\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:

            result["module"] = float(
                match.group(1)
                .replace(",", ".")
            )

        # Pressure angle
        match = re.search(
            r"(?:pressure\s*angle|sudut)"
            r"\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:

            result[
                "pressure_angle"
            ] = float(
                match.group(1)
                .replace(",", ".")
            )

        # Thickness
        match = re.search(
            r"(?:tebal|thickness)"
            r"\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:

            result["thickness"] = float(
                match.group(1)
                .replace(",", ".")
            )

        # Bore
        match = re.search(
            r"(?:bore|lubang)"
            r"\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:

            result["bore"] = float(
                match.group(1)
                .replace(",", ".")
            )

        return result

    # --------------------------------------------------------
    # SHAFT
    # --------------------------------------------------------

    if (
        "shaft" in t
        or "poros" in t
    ):

        return {
            "component_type":
                "stepped_shaft"
        }

    # --------------------------------------------------------
    # CYLINDER
    # --------------------------------------------------------

    if (
        "cylinder" in t
        or "silinder" in t
    ):

        return {
            "component_type":
                "cylinder"
        }

    return None


# ============================================================
# GENERATE
# ============================================================

generate = st.button(
    "🚀 GENERATE ENGINEERING CAD",
    type="primary",
    use_container_width=True
)


# ============================================================
# GENERATION
# ============================================================

if generate:

    parsed = None

    if user_request.strip():

        parsed = ai_parse_request(
            user_request
        )

        if parsed is None:

            parsed = local_parse(
                user_request
            )

    # ========================================================
    # APPLY AI PARAMETERS
    # ========================================================

    if parsed:

        detected = parsed.get(
            "component_type"
        )

        if detected == "gear":

            component = "Gear"

            teeth = int(
                parsed.get(
                    "teeth",
                    teeth
                )
            )

            module = float(
                parsed.get(
                    "module",
                    module
                )
            )

            pressure_angle = float(
                parsed.get(
                    "pressure_angle",
                    pressure_angle
                )
            )

            thickness = float(
                parsed.get(
                    "thickness",
                    thickness
                )
            )

            bore = float(
                parsed.get(
                    "bore",
                    bore
                )
            )

        elif detected == "stepped_shaft":

            component = "Stepped Shaft"

        elif detected == "cylinder":

            component = "Cylinder"


    # ========================================================
    # GEAR
    # ========================================================

    if component == "Gear":

        if not CAD_READY:

            st.error(
                "CAD Engine belum siap."
            )

            st.stop()

        try:

            # ------------------------------------------------
            # BUILD
            # ------------------------------------------------

            gear_model = (
                build_cadquery_gear(
                    teeth,
                    module,
                    pressure_angle,
                    thickness,
                    bore
                )
            )

            # ------------------------------------------------
            # CALCULATIONS
            # ------------------------------------------------

            data = (
                gear_engineering_data(
                    teeth,
                    module,
                    pressure_angle,
                    thickness,
                    bore,
                    material,
                    gear_model
                )
            )

            (
                points,
                pitch_radius,
                base_radius,
                root_radius,
                outer_radius
            ) = (
                create_involute_gear_profile(
                    teeth,
                    module,
                    pressure_angle
                )
            )

            st.success(
                "✅ Engineering gear berhasil dibuat."
            )

            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            c1, c2, c3, c4, c5 = (
                st.columns(5)
            )

            c1.metric(
                "Teeth",
                teeth
            )

            c2.metric(
                "Pitch Ø",
                f"{data['pitch_diameter_mm']:.2f} mm"
            )

            c3.metric(
                "Base Ø",
                f"{data['base_diameter_mm']:.2f} mm"
            )

            c4.metric(
                "Outside Ø",
                f"{data['outside_diameter_mm']:.2f} mm"
            )

            c5.metric(
                "Mass",
                f"{data['mass_kg']:.3f} kg"
            )

            # ------------------------------------------------
            # 3D
            # ------------------------------------------------

            st.subheader(
                "🧊 High Quality 3D CAD"
            )

            show_cadquery_3d(
                gear_model,
                f"DELUXY Gear — {teeth}T",
                MATERIALS[material]["color"]
            )

            # ------------------------------------------------
            # 2D
            # ------------------------------------------------

            st.subheader(
                "📐 2D Engineering Drawing"
            )

            show_gear_2d(
                points,
                bore,
                pitch_radius,
                base_radius,
                root_radius,
                outer_radius
            )

            # ------------------------------------------------
            # ENGINEERING DATA
            # ------------------------------------------------

            st.subheader(
                "📊 Engineering Data"
            )

            d1, d2 = st.columns(2)

            with d1:

                st.write(
                    f"**Module:** "
                    f"{module:.3f} mm"
                )

                st.write(
                    f"**Pressure Angle:** "
                    f"{pressure_angle:.2f}°"
                )

                st.write(
                    f"**Pitch Diameter:** "
                    f"{data['pitch_diameter_mm']:.3f} mm"
                )

                st.write(
                    f"**Base Diameter:** "
                    f"{data['base_diameter_mm']:.3f} mm"
                )

            with d2:

                st.write(
                    f"**Root Diameter:** "
                    f"{data['root_diameter_mm']:.3f} mm"
                )

                st.write(
                    f"**Outside Diameter:** "
                    f"{data['outside_diameter_mm']:.3f} mm"
                )

                st.write(
                    f"**Volume:** "
                    f"{data['volume_mm3']:.2f} mm³"
                )

                st.write(
                    f"**Material:** "
                    f"{material}"
                )

            # ------------------------------------------------
            # EXPORT
            # ------------------------------------------------

            st.subheader(
                "📦 Engineering Exports"
            )

            e1, e2, e3, e4 = (
                st.columns(4)
            )

            with e1:

                try:

                    step_data = (
                        export_step(
                            gear_model
                        )
                    )

                    st.download_button(
                        "⬇️ STEP",
                        step_data,
                        file_name=(
                            f"DELUXY_GEAR_"
                            f"{teeth}T_"
                            f"M{module}.step"
                        ),
                        mime=(
                            "application/step"
                        ),
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"STEP: {e}"
                    )

            with e2:

                try:

                    stl_data = (
                        export_stl(
                            gear_model
                        )
                    )

                    st.download_button(
                        "⬇️ STL",
                        stl_data,
                        file_name=(
                            f"DELUXY_GEAR_"
                            f"{teeth}T_"
                            f"M{module}.stl"
                        ),
                        mime="model/stl",
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"STL: {e}"
                    )

            with e3:

                try:

                    dxf_data = (
                        export_gear_dxf(
                            points,
                            bore
                        )
                    )

                    st.download_button(
                        "⬇️ DXF 2D",
                        dxf_data,
                        file_name=(
                            f"DELUXY_GEAR_"
                            f"{teeth}T_"
                            f"M{module}.dxf"
                        ),
                        mime=(
                            "application/dxf"
                        ),
                        use_container_width=True
                    )

                except Exception as e:

                    st.error(
                        f"DXF: {e}"
                    )

            with e4:

                report = json.dumps(
                    data,
                    indent=4
                )

                st.download_button(
                    "⬇️ JSON REPORT",
                    report,
                    file_name=(
                        f"DELUXY_GEAR_REPORT.json"
                    ),
                    mime="application/json",
                    use_container_width=True
                )


    # ========================================================
    # SHAFT
    # ========================================================

    elif component == "Stepped Shaft":

        if not CAD_READY:

            st.error(
                "CAD Engine belum siap."
            )

            st.stop()

        try:

            shaft_model = (
                build_cadquery_shaft(
                    shaft_length,
                    main_diameter,
                    left_diameter,
                    right_diameter
                )
            )

            st.success(
                "✅ Stepped shaft berhasil dibuat."
            )

            st.subheader(
                "🧊 3D CAD Preview"
            )

            show_cadquery_3d(
                shaft_model,
                "DELUXY Stepped Shaft",
                MATERIALS[material]["color"]
            )

            volume = (
                shaft_model.val().Volume()
            )

            mass = (
                volume *
                MATERIALS[material]["density"]
                / 1_000_000
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "Volume",
                f"{volume:.2f} mm³"
            )

            c2.metric(
                "Mass",
                f"{mass:.3f} kg"
            )

            try:

                step_data = (
                    export_step(
                        shaft_model
                    )
                )

                st.download_button(
                    "⬇️ Download STEP",
                    step_data,
                    file_name=(
                        "DELUXY_STEPPED_SHAFT.step"
                    ),
                    mime="application/step",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"STEP export gagal: {e}"
                )

            try:

                stl_data = (
                    export_stl(
                        shaft_model
                    )
                )

                st.download_button(
                    "⬇️ Download STL",
                    stl_data,
                    file_name=(
                        "DELUXY_STEPPED_SHAFT.stl"
                    ),
                    mime="model/stl",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"STL export gagal: {e}"
                )

        except Exception as e:

            st.error(
                f"❌ Shaft generation gagal: {e}"
            )


    # ========================================================
    # CYLINDER
    # ========================================================

    elif component == "Cylinder":

        if not CAD_READY:

            st.error(
                "CAD Engine belum siap."
            )

            st.stop()

        try:

            cylinder_model = (
                build_cadquery_cylinder(
                    cylinder_diameter,
                    cylinder_height
                )
            )

            st.success(
                "✅ Cylinder berhasil dibuat."
            )

            st.subheader(
                "🧊 3D CAD Preview"
            )

            show_cadquery_3d(
                cylinder_model,
                "DELUXY Cylinder",
                MATERIALS[material]["color"]
            )

            volume = (
                cylinder_model
                .val()
                .Volume()
            )

            mass = (
                volume *
                MATERIALS[material]["density"]
                / 1_000_000
            )

            c1, c2 = st.columns(2)

            c1.metric(
                "Volume",
                f"{volume:.2f} mm³"
            )

            c2.metric(
                "Mass",
                f"{mass:.3f} kg"
            )

            try:

                step_data = (
                    export_step(
                        cylinder_model
                    )
                )

                st.download_button(
                    "⬇️ Download STEP",
                    step_data,
                    file_name=(
                        "DELUXY_CYLINDER.step"
                    ),
                    mime="application/step",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"STEP export gagal: {e}"
                )

            try:

                stl_data = (
                    export_stl(
                        cylinder_model
                    )
                )

                st.download_button(
                    "⬇️ Download STL",
                    stl_data,
                    file_name=(
                        "DELUXY_CYLINDER.stl"
                    ),
                    mime="model/stl",
                    use_container_width=True
                )

            except Exception as e:

                st.error(
                    f"STL export gagal: {e}"
                )

        except Exception as e:

            st.error(
                f"❌ Cylinder generation gagal: {e}"
            )


# ============================================================
# DIAGNOSTICS
# ============================================================

st.divider()

with st.expander(
    "🔍 Engine Diagnostics"
):

    st.write(
        "CadQuery:",
        "READY"
        if CAD_READY
        else "NOT READY"
    )

    st.write(
        "Plotly:",
        "READY"
        if PLOTLY_READY
        else "NOT READY"
    )

    st.write(
        "OpenAI:",
        "AVAILABLE"
        if OPENAI_READY
        else "NOT INSTALLED"
    )

    if CAD_ERROR:

        st.code(
            CAD_ERROR
        )


st.caption(
    "DELUXY.Ai V2 — Parametric Engineering CAD Engine"
)
