import streamlit as st
import os
import json
import math
from typing import Dict, Any, Optional, Tuple, List

# Import deluxy modules
from deluxy.ai.agent import EngineeringAgent
from deluxy.cad.gear import InvoluteGear
from deluxy.cad.shaft import SteppedShaft
from deluxy.cad.cylinder import Cylinder
from deluxy.cad.validator import GeometryValidator
from deluxy.engineering.calculations import GearCalculations, ShaftCalculations, CylinderCalculations
from deluxy.engineering.materials import MaterialDatabase
from deluxy.rendering.renderer3d import Renderer3D
from deluxy.rendering.drawing2d import Drawing2D
from deluxy.export.exporters import ExportSTL, ExportSTEP, ExportDXF, ExportJSON
from deluxy.utils.errors import CADGenerationError, ExportError

# Configuration
st.set_page_config(
    page_title="DELUXY.Ai",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0;
        background: linear-gradient(90deg, #2563eb, #7c3aed);
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "current_design" not in st.session_state:
    st.session_state.current_design = None
if "current_model" not in st.session_state:
    st.session_state.current_model = None
if "design_history" not in st.session_state:
    st.session_state.design_history = []

# Initialize engines
@st.cache_resource
def init_engines():
    agent = EngineeringAgent()
    materials = MaterialDatabase()
    return agent, materials

agent, materials = init_engines()

# Check capabilities
cad_ready = True
try:
    import cadquery as cq
except ImportError:
    cad_ready = False

plotly_ready = True
try:
    import plotly.graph_objects as go
except ImportError:
    plotly_ready = False

ai_ready = agent.is_ready()

# Header
st.markdown('<div class="main-title">💎 DELUXY.Ai</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI Engineering & Parametric CAD Platform</div>', unsafe_allow_html=True)

# Sidebar Status
with st.sidebar:
    st.header("⚙️ System Status")
    
    if cad_ready:
        st.markdown('<div class="status-good">🟢 CAD Engine: READY</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bad">🔴 CAD Engine: NOT READY</div>', unsafe_allow_html=True)
    
    if plotly_ready:
        st.markdown('<div class="status-good">🟢 3D Renderer: READY</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bad">🔴 3D Renderer: NOT READY</div>', unsafe_allow_html=True)
    
    if ai_ready:
        st.markdown('<div class="status-good">🟢 AI Engine: READY</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-bad">🟡 AI Engine: Using Local Parser</div>', unsafe_allow_html=True)
    
    st.divider()
    
    material_name = st.selectbox(
        "Material",
        materials.list_names(),
        index=0
    )
    
    st.divider()
    st.caption("DELUXY.Ai v2.0")
    st.caption("Created by Muhammad Daffa Hendra Winata")

# Main content
st.subheader("🤖 Describe What You Want to Build")

user_request = st.text_area(
    "",
    placeholder="Examples:\n- Buat gear 24 gigi module 2 bore 10mm tebal 8mm\n- Buat shaft panjang 150mm diameter 30mm\n- Buat cylinder diameter 50mm tinggi 100mm",
    height=100
)

component_type = st.selectbox(
    "Component Type",
    ["Gear", "Stepped Shaft", "Cylinder"],
    index=0
)

st.subheader("📐 Engineering Parameters")

if component_type == "Gear":
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        teeth = st.number_input("Teeth", min_value=4, max_value=500, value=24, step=1)
    with col2:
        module = st.number_input("Module", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
    with col3:
        pressure_angle = st.number_input("Pressure Angle", min_value=10.0, max_value=45.0, value=20.0, step=1.0)
    with col4:
        thickness = st.number_input("Thickness", min_value=0.5, max_value=500.0, value=8.0, step=0.5)
    with col5:
        bore = st.number_input("Bore Ø", min_value=0.0, max_value=500.0, value=10.0, step=0.5)
    
    params = {
        "teeth": int(teeth),
        "module": float(module),
        "pressure_angle": float(pressure_angle),
        "thickness": float(thickness),
        "bore": float(bore)
    }

elif component_type == "Stepped Shaft":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        shaft_length = st.number_input("Length", min_value=1.0, value=120.0, step=1.0)
    with col2:
        main_diameter = st.number_input("Main Ø", min_value=0.5, value=25.0, step=0.5)
    with col3:
        left_diameter = st.number_input("Left Ø", min_value=0.5, value=18.0, step=0.5)
    with col4:
        right_diameter = st.number_input("Right Ø", min_value=0.5, value=20.0, step=0.5)
    
    params = {
        "length": float(shaft_length),
        "main_diameter": float(main_diameter),
        "left_diameter": float(left_diameter),
        "right_diameter": float(right_diameter)
    }

else:  # Cylinder
    col1, col2 = st.columns(2)
    with col1:
        cylinder_diameter = st.number_input("Diameter", min_value=0.5, value=30.0, step=0.5)
    with col2:
        cylinder_height = st.number_input("Height", min_value=0.5, value=50.0, step=0.5)
    
    params = {
        "diameter": float(cylinder_diameter),
        "height": float(cylinder_height)
    }

# Generate button
if st.button("🚀 GENERATE ENGINEERING CAD", type="primary", use_container_width=True):
    if not cad_ready:
        st.error("❌ CAD Engine tidak siap. Cek requirements.txt")
        st.stop()
    
    try:
        st.info("⏳ Generating CAD model...")
        
        # Generate CAD
        if component_type == "Gear":
            generator = InvoluteGear()
            generator.generate(params)
            model = generator
            calc_data = GearCalculations.calculate_all(
                params["teeth"],
                params["module"],
                params["pressure_angle"]
            )
        elif component_type == "Stepped Shaft":
            generator = SteppedShaft()
            generator.generate(params)
            model = generator
            calc_data = ShaftCalculations.calculate_all(
                params["length"],
                params["main_diameter"],
                params["left_diameter"],
                params["right_diameter"]
            )
        else:  # Cylinder
            generator = Cylinder()
            generator.generate(params)
            model = generator
            calc_data = CylinderCalculations.calculate_all(
                params["diameter"],
                params["height"]
            )
        
        # Validate
        if not GeometryValidator.validate_solid(model.model):
            errors = GeometryValidator.get_validation_errors(model.model)
            st.error("❌ CAD Geometry Validation Failed")
            for error in errors:
                st.error(f"  • {error}")
            st.stop()
        
        st.success("✅ CAD Model Generated Successfully")
        
        # Store in session
        st.session_state.current_model = model
        st.session_state.current_design = {
            "component": component_type,
            "params": params,
            "material": material_name,
            "calculations": calc_data
        }
        
        # Display metrics
        st.subheader("📊 Key Metrics")
        cols = st.columns(4)
        
        volume = model.model.val().Volume()
        mass = volume * materials.get_density(material_name) / 1_000_000
        
        with cols[0]:
            st.metric("Volume", f"{volume:.2f} mm³")
        with cols[1]:
            st.metric("Mass", f"{mass:.3f} kg")
        with cols[2]:
            st.metric("Material", material_name)
        with cols[3]:
            st.metric("Status", "Valid ✓")
        
        # Display calculations
        if component_type == "Gear":
            st.subheader("⚙️ Gear Calculations")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Pitch Diameter:** {calc_data['pitch_diameter_mm']:.3f} mm")
                st.write(f"**Base Diameter:** {calc_data['base_diameter_mm']:.3f} mm")
                st.write(f"**Addendum:** {calc_data['addendum_mm']:.3f} mm")
            with col2:
                st.write(f"**Outside Diameter:** {calc_data['outside_diameter_mm']:.3f} mm")
                st.write(f"**Root Diameter:** {calc_data['root_diameter_mm']:.3f} mm")
                st.write(f"**Dedendum:** {calc_data['dedendum_mm']:.3f} mm")
        
        # 3D Rendering
        if plotly_ready:
            st.subheader("🧊 3D CAD Preview")
            try:
                vertices, I, J, K = model.get_mesh()
                fig = Renderer3D.create_mesh_plot(
                    vertices, I, J, K,
                    title=f"DELUXY.Ai - {component_type}",
                    color=materials.get(material_name).color
                )
                st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
            except Exception as e:
                st.error(f"3D Rendering failed: {str(e)}")
        
        # 2D Drawing
        if component_type == "Gear" and plotly_ready:
            st.subheader("📐 2D Engineering Drawing")
            try:
                fig_2d = Drawing2D.create_gear_drawing(
                    model.profile_points,
                    params.get("bore", 0),
                    model.pitch_radius,
                    model.base_radius,
                    model.root_radius,
                    model.outer_radius
                )
                st.plotly_chart(fig_2d, use_container_width=True)
            except Exception as e:
                st.error(f"2D Drawing failed: {str(e)}")
        
        # Export section
        st.subheader("📦 Export Engineering Files")
        exp_col1, exp_col2, exp_col3, exp_col4, exp_col5 = st.columns(5)
        
        with exp_col1:
            try:
                step_data = ExportSTEP.export(model.model)
                st.download_button(
                    "⬇️ STEP",
                    step_data,
                    file_name=f"DELUXY_{component_type.replace(' ', '_')}.step",
                    mime="application/step",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"STEP: {str(e)}")
        
        with exp_col2:
            try:
                stl_data = ExportSTL.export(model.model)
                st.download_button(
                    "⬇️ STL",
                    stl_data,
                    file_name=f"DELUXY_{component_type.replace(' ', '_')}.stl",
                    mime="model/stl",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"STL: {str(e)}")
        
        with exp_col3:
            if component_type == "Gear":
                try:
                    dxf_data = ExportDXF.export_profile(
                        model.profile_points,
                        params.get("bore", 0)
                    )
                    st.download_button(
                        "⬇️ DXF",
                        dxf_data,
                        file_name=f"DELUXY_{component_type.replace(' ', '_')}.dxf",
                        mime="application/dxf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"DXF: {str(e)}")
        
        with exp_col4:
            try:
                json_data = ExportJSON.export({
                    "component": component_type,
                    "parameters": params,
                    "material": material_name,
                    "calculations": calc_data,
                    "volume_mm3": volume,
                    "mass_kg": mass
                })
                st.download_button(
                    "⬇️ JSON",
                    json_data,
                    file_name=f"DELUXY_{component_type.replace(' ', '_')}_report.json",
                    mime="application/json",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"JSON: {str(e)}")
    
    except CADGenerationError as e:
        st.error(f"❌ CAD Generation Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")
        with st.expander("📋 Technical Details"):
            st.code(str(e))

# Diagnostics
st.divider()
with st.expander("🔍 System Diagnostics"):
    st.write(f"**CadQuery:** {'READY' if cad_ready else 'NOT READY'}")
    st.write(f"**Plotly:** {'READY' if plotly_ready else 'NOT READY'}")
    st.write(f"**OpenAI API:** {'AVAILABLE' if ai_ready else 'NOT CONFIGURED'}")
    
    if not ai_ready:
        st.info("💡 Set OPENAI_API_KEY environment variable to enable AI parsing")

st.caption("💎 DELUXY.Ai | Created by Muhammad Daffa Hendra Winata")
