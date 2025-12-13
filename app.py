import streamlit as st
from datetime import datetime

# -----------------------------------------------------------
# ESU DEVICE FUNCTIONS (Logic remains untouched)
# -----------------------------------------------------------

def calculate_power_output(set_power_w, load_ohm):
    if load_ohm <= 0:
        return 0
    reference_voltage = (set_power_w * load_ohm) ** 0.5
    delivered = (reference_voltage ** 2) / load_ohm
    return round(delivered, 2)

def calculate_leakage_current(mode, load_ohm):
    if mode == "CUT":
        return round(0.05 + load_ohm * 0.0001, 3)
    if mode == "COAG":
        return round(0.08 + load_ohm * 0.00015, 3)
    return 0.1

def evaluate_test(set_power_w, delivered_power, leakage, max_leakage, tolerance):
    low_limit = set_power_w * (1 - tolerance)
    high_limit = set_power_w * (1 + tolerance)

    power_ok = low_limit <= delivered_power <= high_limit
    leakage_ok = leakage <= max_leakage

    power_warning = low_limit * 1.05 <= delivered_power <= high_limit * 0.95
    leakage_warning = max_leakage * 0.9 <= leakage <= max_leakage

    overall = "PASS" if power_ok and leakage_ok else "FAIL"

    return {
        "power_check": "PASS" if power_ok else "FAIL",
        "power_warning": "WARNING" if power_warning else "OK",
        "leakage_check": "PASS" if leakage_ok else "FAIL",
        "leakage_warning": "WARNING" if leakage_warning else "OK",
        "overall": overall
    }

# -----------------------------------------------------------
# WEB UI (Clean, Minimalist Design)
# -----------------------------------------------------------

def main():
    st.set_page_config(page_title="ESU Testing System")

    st.title("Electrosurgical Unit (ESU) Tester")
    st.markdown("---")

    # --- SECTION 1: CONFIGURATION ---
    st.subheader("Test Configuration")
    
    # Grid layout for inputs
    col1, col2 = st.columns(2)
    with col1:
        test_name = st.text_input("Test Reference Name", "ESU Power Test")
        mode = st.selectbox("Operating Mode", ["CUT", "COAG"])
        set_power = st.number_input("Set Power (Watts)", 5, 400, 150)
    
    with col2:
        load = st.number_input("Load Resistance (Ohms)", 10, 500, 200)
        max_leakage = st.number_input("Max Allowed Leakage (A)", 0.01, 0.5, 0.1)
        tolerance_percent = st.slider("Power Tolerance (%)", 5, 30, 15)

    st.write("") 
    if st.button("Run Performance Test", use_container_width=True):
        st.markdown("---")
        
        # Calculations
        tolerance = tolerance_percent / 100
        delivered = calculate_power_output(set_power, load)
        leakage = calculate_leakage_current(mode, load)
        result = evaluate_test(set_power, delivered, leakage, max_leakage, tolerance)

        # --- SECTION 2: SUMMARY STATUS ---
        if result["overall"] == "PASS":
            st.success(f"{test_name}: PASS")
        else:
            st.error(f"{test_name}: FAIL")

        # --- SECTION 3: METRICS ---
        st.write("#### Measured Values")
        m1, m2, m3 = st.columns(3)
        
        # Calculate power delta
        p_delta = round(delivered - set_power, 2)
        
        m1.metric("Delivered Power", f"{delivered} W", f"{p_delta} W")
        m2.metric("Leakage Current", f"{leakage} A", f"Limit: {max_leakage} A", delta_color="inverse")
        m3.metric("Load", f"{load} Ohms")

        st.divider()

        # --- SECTION 4: DETAILED LOGS ---
        st.write("#### Detailed Diagnostics")
        log_col1, log_col2 = st.columns(2)
        
        with log_col1:
            st.write("**Power Check:**")
            st.code(result['power_check'])
            st.write("**Power Warning:**")
            st.code(result['power_warning'])
            
        with log_col2:
            st.write("**Leakage Check:**")
            st.code(result['leakage_check'])
            st.write("**Leakage Warning:**")
            st.code(result['leakage_warning'])

        # Footer
        st.caption(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()