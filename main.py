import streamlit as st
from prefixed import Float

from application.materials import ALL_MATERIALS
from application.traces import TraceCalculator



def main():
    st.set_page_config(page_title="PCB Heater Generator", layout="wide")
    st.title("PCB Heater Generator")

    with st.sidebar:
        with st.expander("General", expanded=True):
            col1, col2 = st.columns(2)
            voltage = col1.number_input("Voltage (V)", 1.0, 50.0, 12.0, 1.0)
            max_current = col2.number_input("Max. Current (A)", 1.0, 36.0, 10.0, 1.0)
            temperature_rise = st.number_input("Temperature Rise (°C)", 10.0, 500.0, 225.0, 5.0)

        with st.expander("PCB Settings", True):
            material = st.selectbox("Material", ALL_MATERIALS, format_func=lambda o: o.name)
            thickness = st.selectbox("Thickness", [1, 2], format_func=lambda o: f"{o} oz/ft²")*0.035 # in mm
            clearance = st.number_input("Clearance (mm)", 0.0, 10.0, 0.2, 0.1)
            pcb_height = st.number_input("Height (mm)", 10.0, 400.0, 100.0, 5.0)

    trace = TraceCalculator(material, temperature_rise, thickness, max_current)

    minimal_track_length = trace.length_from_resistance(voltage/max_current)
    n, track_length, resistance, current, pcb_width = trace.generate_serpentine(
        height=pcb_height - 2*clearance,
        voltage=voltage,
        clearance=clearance,
        min_length=minimal_track_length
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Power", f"{Float(voltage*current):!.1h}W", f"Max: {Float(max_current*voltage):!.1h}W", delta_color="off")
    col2.metric("Electrical Resistance", f"{Float(resistance):!.2h}Ω", f"Min: {Float(voltage/max_current):!.2h}Ω", delta_color="off")
    col3.metric("Approx. Current", f"{Float(current):!.2h}A")
    col4.metric("Number of serpentines", n)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Track Length", f"{track_length:.1f} mm", f"Min: {minimal_track_length:.1f} mm", delta_color="off")
    col2.metric("Trace Width", f"{trace.width:.4f} mm")
    col3.metric("PCB Width", f"{pcb_width:.1f} mm")
    col4.metric("PCB Height", f"{pcb_height:.1f} mm")

    st.download_button("Download KiCAD Footprint", bytes(), "footprint.kicad_mod")



if __name__ == "__main__":
    main()
