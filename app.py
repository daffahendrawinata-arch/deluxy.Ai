import streamlit as st
import math
import os
import tempfile
import json

# ============================================================
# DELUXY.Ai ENGINE
# AI Assisted Parametric CAD Generator
# ============================================================

st.set_page_config(
    page_title="DELUXY.Ai CAD Engine",
    page_icon="💎",
    layout="wide"
)

# ============================================================
# OPTIONAL CAD ENGINE
# ============================================================

try:
    import cadquery as cq
    CAD_READY = True
    CAD_ERROR = ""
except Exception as e:
    CAD_READY = False
    CAD_ERROR = str(e)

# ============================================================
# OPTIONAL PLOTLY
# ============================================================

try:
    import plotly.graph_objects as go
    PLOTLY_READY = True
except Exception:
    PLOTLY_READY = False

# ============================================================
# OPTIONAL OPENAI
# ============================================================

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
    font-size: 2.8rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #64748b;
    margin-bottom: 25px;
}

.status-good {
    padding: 16px;
    border-radius: 12px;
    background: #dcfce7;
    color: #166534;
    font-weight: 700;
}

.status-bad {
    padding: 16px;
    border-radius: 12px;
    background: #fee2e2;
    color: #991b1b;
    font-weight: 700;
}

.card {
    padding: 20px;
    border-radius: 15px;
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
    '<div class="subtitle">Parametric AI-Assisted CAD Generator</div>',
    unsafe_allow_html=True
)


# ============================================================
# ENGINE STATUS
# ============================================================

with st.sidebar:

    st.header("⚙️ DELUXY Engine")

    if CAD_READY:
        st.markdown(
            '<div class="status-good">🟢 CAD Engine: READY</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-bad">🔴 CAD Engine: NOT READY</div>',
            unsafe_allow_html=True
        )

        st.error(CAD_ERROR)

    if PLOTLY_READY:
        st.success("🟢 3D Renderer: READY")
    else:
        st.error("🔴 Plotly: NOT READY")

    st.divider()

    material = st.selectbox(
        "Material",
        [
            "Steel",
            "Stainless Steel",
            "Aluminium",
            "Brass",
            "Copper",
            "Titanium",
            "Plastic"
        ]
    )

    st.divider()

    st.caption("DELUXY.Ai CAD Engine")
    st.caption("Parametric engineering model generator")


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
# TEXT REQUEST
# ============================================================

st.subheader("🤖 What do you want to build?")

user_request = st.text_area(
    "",
    placeholder=(
        "Contoh:\n"
        "Buatkan gear 24 gigi, module 2, bore 10 mm, "
        "tebal 8 mm, pressure angle 20 derajat"
    ),
    height=120
)


# ============================================================
# COMPONENT SELECTOR
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
# ENGINEERING PARAMETERS
# ============================================================

st.subheader("📐 Engineering Parameters")

if component == "Gear":

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        teeth = st.number_input(
            "Jumlah Gigi",
            min_value=4,
            max_value=300,
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
            max_value=200.0,
            value=8.0,
            step=0.5
        )

    with c5:
        bore = st.number_input(
            "Bore",
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
            "Main Diameter",
            min_value=0.5,
            value=25.0,
            step=0.5
        )

    with c3:
        left_diameter = st.number_input(
            "Left Diameter",
            min_value=0.5,
            value=18.0,
            step=0.5
        )

    right_diameter = st.number_input(
        "Right Diameter",
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
# GEAR GEOMETRY
# ============================================================

def create_gear_polygon(
    teeth,
    module,
    pressure_angle,
    bore
):
    """
    Membuat profil gear parametrik yang valid untuk CadQuery.

    Menghindari duplicate consecutive points yang dapat membuat
    wire OpenCascade menjadi invalid.
    """

    teeth = int(teeth)
    module = float(module)
    pressure_angle = float(pressure_angle)
    bore = float(bore)

    if teeth < 4:
        raise ValueError("Jumlah gigi minimal 4.")

    if module <= 0:
        raise ValueError("Module harus lebih besar dari 0.")

    pitch_radius = module * teeth / 2.0

    addendum = module
    dedendum = 1.25 * module

    outer_radius = pitch_radius + addendum
    root_radius = pitch_radius - dedendum

    if root_radius <= 0:
        raise ValueError("Parameter gear menghasilkan root diameter <= 0.")

    bore_radius = bore / 2.0

    if bore_radius >= root_radius:
        raise ValueError(
            f"Bore {bore:.2f} mm terlalu besar. "
            f"Bore harus lebih kecil dari root diameter "
            f"{root_radius * 2:.2f} mm."
        )

    points = []

    tooth_pitch = 2.0 * math.pi / teeth

    # Lebar gigi pada area pitch
    tooth_width = tooth_pitch * 0.42

    for i in range(teeth):

        center = i * tooth_pitch

        a1 = center - tooth_pitch / 2.0
        a2 = center - tooth_width / 2.0
        a3 = center + tooth_width / 2.0
        a4 = center + tooth_pitch / 2.0

        tooth_points = [
            (
                root_radius * math.cos(a1),
                root_radius * math.sin(a1)
            ),
            (
                root_radius * math.cos(a2),
                root_radius * math.sin(a2)
            ),
            (
                outer_radius * math.cos(a2),
                outer_radius * math.sin(a2)
            ),
            (
                outer_radius * math.cos(a3),
                outer_radius * math.sin(a3)
            ),
            (
                root_radius * math.cos(a3),
                root_radius * math.sin(a3)
            )
        ]

        # Tambahkan titik terakhir hanya jika tidak sama
        # dengan titik sebelumnya.
        for p in tooth_points:

            if not points or p != points[-1]:
                points.append(p)

    # Hapus duplicate terakhir jika ada
    # akibat periodic closure.
    cleaned = []

    for p in points:

        if not cleaned:
            cleaned.append(p)
            continue

        dx = p[0] - cleaned[-1][0]
        dy = p[1] - cleaned[-1][1]

        if math.hypot(dx, dy) > 1e-9:
            cleaned.append(p)

    return (
        cleaned,
        root_radius,
        outer_radius,
        bore_radius
    )

# ============================================================
# CADQUERY GEAR
# ============================================================

def build_cadquery_gear(
    teeth,
    module,
    pressure_angle,
    thickness,
    bore
):
    """
    Membuat solid gear menggunakan CadQuery.

    Profil dibuat sebagai closed polygon kemudian di-extrude.
    Bore dibuat sebagai solid cylinder dan dipotong menggunakan
    boolean cut agar lebih stabil daripada .hole().
    """

    points, root_radius, outer_radius, bore_radius = \
        create_gear_polygon(
            teeth,
            module,
            pressure_angle,
            bore
        )

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if thickness <= 0:
        raise ValueError(
            "Thickness harus lebih besar dari 0."
        )

    if len(points) < 8:
        raise ValueError(
            "Profil gear tidak memiliki cukup titik."
        )

    # --------------------------------------------------------
    # CREATE GEAR BODY
    # --------------------------------------------------------

    gear = (
        cq.Workplane("XY")
        .polyline(points)
        .close()
        .extrude(thickness)
    )

    # Pastikan solid berhasil dibuat
    if gear.val().isNull():
        raise ValueError(
            "Gear body menghasilkan solid kosong."
        )

    # --------------------------------------------------------
    # CENTRAL BORE
    # --------------------------------------------------------

    if bore > 0:

        bore_tool = (
            cq.Workplane("XY")
            .circle(bore / 2.0)
            .extrude(thickness)
        )

        gear = gear.cut(bore_tool)

    return gear
# ============================================================
# CADQUERY SHAFT
# ============================================================

def build_cadquery_shaft(
    length,
    main_diameter,
    left_diameter,
    right_diameter
):

    left_length = length * 0.25
    main_length = length * 0.50
    right_length = length * 0.25

    shaft = (
        cq.Workplane("XY")
        .circle(left_diameter / 2)
        .extrude(left_length)
    )

    shaft = (
        shaft
        .faces(">Z")
        .workplane()
        .circle(main_diameter / 2)
        .extrude(main_length)
    )

    shaft = (
        shaft
        .faces(">Z")
        .workplane()
        .circle(right_diameter / 2)
        .extrude(right_length)
    )

    return shaft


# ============================================================
# CADQUERY CYLINDER
# ============================================================

def build_cadquery_cylinder(
    diameter,
    height
):

    return (
        cq.Workplane("XY")
        .circle(diameter / 2)
        .extrude(height)
    )


# ============================================================
# PLOTLY MESH GENERATOR
# ============================================================

def polygon_to_mesh(points, height):

    n = len(points)

    vertices = []

    # Bottom
    for x, y in points:
        vertices.append((x, y, 0))

    # Top
    for x, y in points:
        vertices.append((x, y, height))

    # Center points
    bottom_center = len(vertices)
    vertices.append((0, 0, 0))

    top_center = len(vertices)
    vertices.append((0, 0, height))

    I = []
    J = []
    K = []

    # Bottom and top surfaces
    for i in range(n):

        j = (i + 1) % n

        # Bottom
        I.append(bottom_center)
        J.append(j)
        K.append(i)

        # Top
        I.append(top_center)
        J.append(n + i)
        K.append(n + j)

    # Side walls
    for i in range(n):

        j = (i + 1) % n

        b1 = i
        b2 = j

        t1 = n + i
        t2 = n + j

        I.append(b1)
        J.append(b2)
        K.append(t1)

        I.append(b2)
        J.append(t2)
        K.append(t1)

    return vertices, I, J, K


# ============================================================
# GEAR MESH WITH BORE
# ============================================================

def gear_mesh(
    teeth,
    module,
    pressure_angle,
    thickness,
    bore
):

    points, root_radius, outer_radius, bore_radius = \
        create_gear_polygon(
            teeth,
            module,
            pressure_angle,
            bore
        )

    vertices, I, J, K = polygon_to_mesh(
        points,
        thickness
    )

    # The gear body is already detailed.
    # Bore visualization is created separately.
    return vertices, I, J, K, bore_radius


# ============================================================
# CYLINDER MESH
# ============================================================

def cylinder_mesh(radius, height, segments=96):

    points = []

    for i in range(segments):

        a = 2 * math.pi * i / segments

        points.append(
            (
                radius * math.cos(a),
                radius * math.sin(a)
            )
        )

    return polygon_to_mesh(
        points,
        height
    )


# ============================================================
# SHAFT MESH
# ============================================================

def stepped_shaft_mesh(
    length,
    main_diameter,
    left_diameter,
    right_diameter,
    segments=96
):

    vertices = []
    faces_i = []
    faces_j = []
    faces_k = []

    sections = [
        (0, left_diameter / 2),
        (length * 0.25, left_diameter / 2),
        (length * 0.25, main_diameter / 2),
        (length * 0.75, main_diameter / 2),
        (length * 0.75, right_diameter / 2),
        (length, right_diameter / 2)
    ]

    # rings
    for x, radius in sections:

        for i in range(segments):

            a = 2 * math.pi * i / segments

            vertices.append(
                (
                    x,
                    radius * math.cos(a),
                    radius * math.sin(a)
                )
            )

    ring_count = len(sections)

    for r in range(ring_count - 1):

        for i in range(segments):

            j = (i + 1) % segments

            a = r * segments + i
            b = r * segments + j

            c = (r + 1) * segments + i
            d = (r + 1) * segments + j

            faces_i.append(a)
            faces_j.append(b)
            faces_k.append(c)

            faces_i.append(b)
            faces_j.append(d)
            faces_k.append(c)

    return vertices, faces_i, faces_j, faces_k


# ============================================================
# DISPLAY MESH
# ============================================================

def show_mesh(
    vertices,
    I,
    J,
    K,
    title,
    material_color
):

    if not PLOTLY_READY:
        st.error(
            "Plotly belum tersedia. "
            "Tambahkan plotly ke requirements.txt"
        )
        return

    x = [v[0] for v in vertices]
    y = [v[1] for v in vertices]
    z = [v[2] for v in vertices]

    fig = go.Figure(
        data=[
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
                    diffuse=0.8,
                    specular=0.5,
                    roughness=0.35,
                    fresnel=0.15
                ),
                lightposition=dict(
                    x=100,
                    y=100,
                    z=200
                )
            )
        ]
    )

    fig.update_layout(
        title=title,
        height=650,
        margin=dict(
            l=0,
            r=0,
            t=50,
            b=0
        ),
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
                    x=1.5,
                    y=1.5,
                    z=1.2
                )
            )
        ),
        paper_bgcolor="#0b1020",
        plot_bgcolor="#0b1020"
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
# OPENAI PARSER
# ============================================================

def ai_parse_request(text):

    api_key = None

    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key or not OPENAI_READY:
        return None

    try:

        client = OpenAI(
            api_key=api_key
        )

        system_prompt = """
You are DELUXY.Ai engineering CAD parser.

Convert natural language engineering requests
into strict JSON.

Allowed component_type:
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

Return JSON only.
No markdown.
No explanation.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        content = response.choices[0].message.content

        return json.loads(content)

    except Exception:
        return None


# ============================================================
# SIMPLE LOCAL AI PARSER
# ============================================================

def local_parse(text):

    t = text.lower()

    result = {}

    # ---------------- GEAR ----------------

    if (
        "gear" in t
        or "roda gigi" in t
        or "roda gigi" in t
        or "gir" in t
    ):

        result["component_type"] = "gear"

        m = None

        # teeth
        import re

        match = re.search(
            r"(\d+)\s*(?:gigi|teeth)",
            t
        )

        if match:
            result["teeth"] = int(match.group(1))

        # module
        match = re.search(
            r"module\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:
            result["module"] = float(
                match.group(1).replace(",", ".")
            )

        # pressure angle
        match = re.search(
            r"([0-9]+(?:[.,][0-9]+)?)\s*(?:derajat|degree|deg).*?(?:pressure|sudut)",
            t
        )

        if not match:

            match = re.search(
                r"(?:pressure\s*angle|sudut)\s*([0-9]+(?:[.,][0-9]+)?)",
                t
            )

        if match:
            result["pressure_angle"] = float(
                match.group(1).replace(",", ".")
            )

        # thickness
        match = re.search(
            r"(?:tebal|thickness)\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:
            result["thickness"] = float(
                match.group(1).replace(",", ".")
            )

        # bore
        match = re.search(
            r"(?:bore|lubang|diameter lubang)\s*([0-9]+(?:[.,][0-9]+)?)",
            t
        )

        if match:
            result["bore"] = float(
                match.group(1).replace(",", ".")
            )

        return result

    # ---------------- SHAFT ----------------

    if (
        "shaft" in t
        or "poros" in t
    ):

        result["component_type"] = "stepped_shaft"

        return result

    # ---------------- CYLINDER ----------------

    if (
        "cylinder" in t
        or "silinder" in t
    ):

        result["component_type"] = "cylinder"

        return result

    return None


# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    "🚀 GENERATE CAD",
    type="primary",
    use_container_width=True
)


# ============================================================
# GENERATION
# ============================================================

if generate:

    parsed = None

    # Try OpenAI first
    if user_request.strip():

        parsed = ai_parse_request(
            user_request
        )

        # fallback local parser
        if parsed is None:

            parsed = local_parse(
                user_request
            )

    # --------------------------------------------------------
    # USE PARSED REQUEST
    # --------------------------------------------------------

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
                "CAD Engine belum siap. "
                "CadQuery gagal di-import."
            )

            st.stop()

        try:

            # Build real CadQuery geometry
            gear_model = build_cadquery_gear(
                teeth,
                module,
                pressure_angle,
                thickness,
                bore
            )

            st.success(
                "✅ CadQuery berhasil membuat model gear."
            )

            # Geometry values
            pitch_diameter = teeth * module
            outer_diameter = pitch_diameter + (
                2 * module
            )

            root_diameter = pitch_diameter - (
                2 * 1.25 * module
            )

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "Teeth",
                teeth
            )

            col2.metric(
                "Pitch Ø",
                f"{pitch_diameter:.2f} mm"
            )

            col3.metric(
                "Outer Ø",
                f"{outer_diameter:.2f} mm"
            )

            col4.metric(
                "Bore Ø",
                f"{bore:.2f} mm"
            )

            # Preview
            st.subheader(
                "🧊 3D CAD Preview"
            )

            vertices, I, J, K, bore_radius = \
                gear_mesh(
                    teeth,
                    module,
                    pressure_angle,
                    thickness,
                    bore
                )

            show_mesh(
                vertices,
                I,
                J,
                K,
                f"Gear — {teeth} Teeth",
                MATERIALS[material]["color"]
            )

            # ------------------------------------------------
            # EXPORT STL
            # ------------------------------------------------

            tmp = tempfile.NamedTemporaryFile(
                suffix=".stl",
                delete=False
            )

            tmp.close()

            cq.exporters.export(
                gear_model,
                tmp.name
            )

            with open(
                tmp.name,
                "rb"
            ) as f:

                st.download_button(
                    label="⬇️ Download STL",
                    data=f.read(),
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
                f"❌ Gear generation gagal: {e}"
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

            shaft_model = build_cadquery_shaft(
                shaft_length,
                main_diameter,
                left_diameter,
                right_diameter
            )

            st.success(
                "✅ Stepped shaft berhasil dibuat."
            )

            st.subheader(
                "🧊 3D CAD Preview"
            )

            vertices, I, J, K = \
                stepped_shaft_mesh(
                    shaft_length,
                    main_diameter,
                    left_diameter,
                    right_diameter
                )

            show_mesh(
                vertices,
                I,
                J,
                K,
                "Stepped Shaft",
                MATERIALS[material]["color"]
            )

            tmp = tempfile.NamedTemporaryFile(
                suffix=".stl",
                delete=False
            )

            tmp.close()

            cq.exporters.export(
                shaft_model,
                tmp.name
            )

            with open(
                tmp.name,
                "rb"
            ) as f:

                st.download_button(
                    label="⬇️ Download STL",
                    data=f.read(),
                    file_name="DELUXY_STEPPED_SHAFT.stl",
                    mime="model/stl",
                    use_container_width=True
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

            cylinder_model = build_cadquery_cylinder(
                cylinder_diameter,
                cylinder_height
            )

            st.success(
                "✅ Cylinder berhasil dibuat."
            )

            st.subheader(
                "🧊 3D CAD Preview"
            )

            vertices, I, J, K = \
                cylinder_mesh(
                    cylinder_diameter / 2,
                    cylinder_height
                )

            show_mesh(
                vertices,
                I,
                J,
                K,
                "Cylinder",
                MATERIALS[material]["color"]
            )

            tmp = tempfile.NamedTemporaryFile(
                suffix=".stl",
                delete=False
            )

            tmp.close()

            cq.exporters.export(
                cylinder_model,
                tmp.name
            )

            with open(
                tmp.name,
                "rb"
            ) as f:

                st.download_button(
                    label="⬇️ Download STL",
                    data=f.read(),
                    file_name="DELUXY_CYLINDER.stl",
                    mime="model/stl",
                    use_container_width=True
                )

        except Exception as e:

            st.error(
                f"❌ Cylinder generation gagal: {e}"
            )


# ============================================================
# INFORMATION
# ============================================================

st.divider()

with st.expander("🔍 Diagnostics"):

    st.write(
        "CadQuery:",
        "READY" if CAD_READY else "NOT READY"
    )

    st.write(
        "Plotly:",
        "READY" if PLOTLY_READY else "NOT READY"
    )

    st.write(
        "OpenAI:",
        "AVAILABLE" if OPENAI_READY else "NOT INSTALLED"
    )

    if CAD_ERROR:
        st.code(CAD_ERROR)

st.caption(
    "DELUXY.Ai — Parametric CAD Engine"
)
