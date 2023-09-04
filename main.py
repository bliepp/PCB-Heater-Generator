import streamlit as st
from prefixed import Float

from application import materials
from application.traces import TraceCalculator
from application.constants import MILS_TO_MM, MM_TO_MILS



st.set_page_config(page_title="PCB Heater Generator", layout="wide")
st.title("PCB Heater Generator")



# trace
with st.sidebar:
    with st.expander("General", expanded=True):
        col1, col2 = st.columns(2)
        voltage = col1.number_input("Voltage (V)", 1.0, 50.0, 12.0, 1.0)
        current = col2.number_input("Current (A)", 1.0, 36.0, 5.0, 1.0)
        temperature_rise = st.number_input("Temperature Rise (°C)", 10.0, 300.0, 180.0, 10.0)

    with st.expander("PCB Settings", True):
        material = st.selectbox("Material", materials.ALL, format_func=lambda o: o.name)
        thickness = st.selectbox("Thickness", [1, 2], format_func=lambda o: f"{o} oz/ft²")*0.035 # in mm
        #col1, col2 = st.columns(2)
        #pcb_width = col1.number_input("Width (mm)", 10.0, 400.0, 100.0, 5.0)
        #pcb_height = col2.number_input("Height (mm)", 10.0, 400.0, 100.0, 5.0)

    with st.expander("Trace Generation"):
        style = st.selectbox("Style", ["sharp", "classic", "round"], format_func=lambda o: o.capitalize())
        clearance = st.number_input("Minimum Clearance (mm)", 0.0, 10.0, 0.2, 0.1)


trace = TraceCalculator(material, temperature_rise, thickness, current)
resistance = voltage/current
power_loss = current*voltage

track_length = trace.length_from_resistance(resistance)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Power", f"{Float(power_loss):!.1h}W")
col2.metric("Electrical Resistance", f"{Float(resistance):!.2h}Ω")
col3.metric("Trace Width", f"{trace.width:.4f} mm")
col4.metric("Track Length", f"{track_length:.1f} mm")

st.download_button("Download KiCAD Footprint", bytes(), "footprint.kicad_mod")
