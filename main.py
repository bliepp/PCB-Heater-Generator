from datetime import date
from functools import partial

import streamlit as st
from prefixed import Float

from application.constants import PAGE_TITLE, PAGE_LAYOUT
from application.materials import ALL_MATERIALS
from application.traces import TraceCalculator
from application.footprint import Footprint, KiCADFootprint



def generate_serpentine(footprint: Footprint, n: int, pcb_height: float, trace_width: float, clearance: float) -> bytes|str:
    delta = trace_width+clearance
    inner_width = (n-1)*delta

    offset_x, offset_y = -inner_width/2, -(pcb_height - 2*clearance)/2

    # start line that brigeds the delta to serpentines
    footprint.add_line(
        (offset_x, offset_y),
        (offset_x, delta+offset_y),
        trace_width,
    )

    # vertical lines of serpentines
    for i in range(n):
        footprint.add_line(
            (i*delta + offset_x, delta + offset_y),
            (i*delta + offset_x, pcb_height - 2*clearance + offset_y),
            trace_width,
        )

    # horizontal lines of serpentines
    for i in range(n-1):
        upper = i % 2 == 1
        y = upper*delta + (not upper)*(pcb_height-2*clearance)
        footprint.add_line(
            (i*delta + offset_x, y + offset_y),
            ((i+1)*delta + offset_x, y + offset_y),
            trace_width,
        )

    # brigde from serpentines to end line
    footprint.add_line(
        (inner_width + offset_x, delta + offset_y),
        (inner_width + offset_x, offset_y),
        trace_width,
    )

    # end line
    footprint.add_line(
        (delta + offset_x, offset_y),
        (inner_width + offset_x, offset_y),
        trace_width,
    )

    # pads
    footprint.add_smd_pad("1", 0.25,
        (offset_x, offset_y),
        (trace_width, trace_width),
    )
    footprint.add_smd_pad("2", 0.25,
        (delta + offset_x, offset_y),
        (trace_width, trace_width),
    )

    # silkscreen
    footprint.add_rectangle(
        (-clearance + offset_x, -clearance + offset_y),
        (i*delta + 3*clearance + offset_x, pcb_height - clearance + offset_y),
        0.5,
    )

    return footprint.evaluate()



kicad_footprint = partial(generate_serpentine, KiCADFootprint(
        "heater", int(str(date.today()).replace("-", ""))
    ))



def main():
    st.set_page_config(
        page_title=PAGE_TITLE,
        initial_sidebar_state="expanded",
        layout=PAGE_LAYOUT,
    )
    st.title(PAGE_TITLE)

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

    min_resistance = voltage/max_current
    minimal_track_length = trace.length_from_resistance(min_resistance)
    n, track_length = trace.serpentine_data(
        height=pcb_height - 2*clearance,
        clearance=clearance,
        min_length=minimal_track_length
    )
    pcb_width = (n-1)*(clearance + trace.width) + 2*clearance

    resistance = trace.resistance_from_length(track_length)
    current = voltage/resistance

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Power", f"{Float(voltage*current):!.1h}W", f"Max: {Float(max_current*voltage):!.1h}W", delta_color="off")
    col2.metric("Electrical Resistance", f"{Float(resistance):!.2h}Ω", f"Min: {Float(min_resistance):!.2h}Ω", delta_color="off")
    col3.metric("Approx. Current", f"{Float(current):!.2h}A")
    col4.metric("Number of serpentines", n)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Track Length", f"{track_length:.1f} mm", f"Min: {minimal_track_length:.1f} mm", delta_color="off")
    col2.metric("Trace Width", f"{trace.width:.4f} mm")
    col3.metric("PCB Width", f"{pcb_width:.1f} mm")
    col4.metric("PCB Height", f"{pcb_height:.1f} mm")

    st.download_button(
        "Download KiCAD Footprint",
        kicad_footprint(n, pcb_height, trace.width, clearance),
        "footprint.kicad_mod",
        use_container_width=True,
    )



if __name__ == "__main__":
    main()
