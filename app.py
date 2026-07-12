import streamlit as st
import pandas as pd
import plotly.express as px
from ibm_watsonx_ai.foundation_models import ModelInference

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Intelliwaste Planner", layout="wide")

# 2. MODERN GLASSMORPHISM DESIGN SYSTEM (CSS)
st.markdown("""
    <style>
    /* Gradient Background */
    .stApp { 
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f62fe 100%);
    }
    
    /* Glassmorphism Cards */
    .report-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    
    /* Force ALL text to be white */
    h1, h2, h3, h4, p, label, .stMarkdown, .stText, .stMetricValue, .stMetricLabel { 
        color: #ffffff !important; 
    }
    
    /* Force sidebar text specifically */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0f62fe !important; 
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SETUP
API_KEY = "YOUR_API_KEY" 
PROJECT_ID = "d906142e-82d8-40d5-a1e1-6b387249fac2"

model = ModelInference(
    model_id="meta-llama/llama-3-3-70b-instruct",
    credentials={"apikey": API_KEY, "url": "https://region.ml.cloud.ibm.com"},
    project_id=PROJECT_ID
)

# 4. HEADER
st.title("🌱 Intelliwaste Event Planner")
st.markdown("---")

# 5. SIDEBAR INPUTS
with st.sidebar:
    st.header("⚙️ Event Parameters")
    guests = st.number_input("Number of Guests", min_value=1, value=5000)
    duration = st.number_input("Duration (hours)", min_value=1, value=24)
    event_type = st.selectbox("Event Type", ["Wedding", "Corporate Event", "Conference", "Birthday Party", "others"])
    menu_type = st.selectbox("Menu Type", ["Buffet", "Plated", "Cocktail", "others"])
    climate = st.selectbox("Climate", ["Summer", "Winter", "Rainy", "Heavy rain"])
    menu = st.text_area("Menu Details (with quantities in kilograms,grams)", 
                        placeholder="e.g., Chicken-200g, Rice-150g, Veg Salad-100g")
    dietary_preferences = st.radio("Dietary Preference", ["Veg", "Non-veg", "Mixed"])
    
    generate_btn = st.button("Generate Sustainability Plan", use_container_width=True)

# 6. MAIN LOGIC
if not generate_btn:
    st.markdown("### Welcome")
    st.write("Configure your event parameters in the sidebar and click **'Generate Sustainability Plan'** to view your professional report.")
else:
    # Calculations Function
    # 1. Parsing Function
    def parse_menu_weight(menu_text):
        import re
    # Extract numbers followed by 'kg' or 'g'
        matches = re.findall(r'(\d+)\s*(kg|g)', menu_text, re.IGNORECASE)
        total_kg = 0
        for amount, unit in matches:
            val = float(amount)
            if unit.lower() == 'g':
                total_kg += val / 1000  # Convert grams to kg
            else:
                total_kg += val        # Keep as kg
        return total_kg

    # 2. Calculate metrics
    total_food_weight = parse_menu_weight(menu)
    
    # Dictionary to define waste rates
    waste_rates = {
        "Buffet": 0.30,
        "Plated": 0.15,
        "Family Style": 0.25
    }
    
    # Get the specific rate for the selected menu type; default to 0.20 if not found
    current_waste_rate = waste_rates.get(menu_type, 0.20)
    
    # Calculate using the dynamic rate
    total_waste = total_food_weight * current_waste_rate
    recovery_potential = total_waste * 0.6
    carbon_footprint = total_waste * 2.5
    # AI Report Generation (Fixed Logic)
    prompt = f"""
    Create a detailed waste management plan for a {event_type} event.
    Service Style: {menu_type}
    Dietary Preference: {dietary_preferences}
    Menu Details: {menu}

    Please include:
    1. Waste estimation (based on the provided quantities).
    2. Carbon footprint analysis (Note: The footprint is {carbon_footprint:.1f} kg CO2e).
    3. Specific recommendations for {dietary_preferences} food waste reduction.
    4. Leftover strategy.
    """
    
    with st.spinner("Analyzing data and calculating impact..."):
        ai_response = model.generate_text(prompt=prompt, params={"max_new_tokens": 10000})
    
    # A. Display Metrics
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.subheader("📊 Event Sustainability Report")
    col1, col2, col3, = st.columns(3)
    with col1:
        st.metric("Est. Total Waste", f"{total_waste:.1f} kg")
    with col2:
        st.metric("Recovery Potential", f"{recovery_potential:.1f} kg")
    with col3:
        st.metric("Carbon Footprint", f"{carbon_footprint:.1f} kg CO2e")

    # B. Professional Chart
    df = pd.DataFrame({"Category": ["Total Waste", "Recovery Potential"], "Amount (kg)": [total_waste, recovery_potential]})
    
    fig = px.bar(df, x="Category", y="Amount (kg)", color="Category", 
                 color_discrete_map={"Total Waste": "#fbbf24", "Recovery Potential": "#2dd4bf"})
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", size=14),
        title_font=dict(color="white"),
        xaxis=dict(title=dict(font=dict(color="white"))),
        yaxis=dict(title=dict(font=dict(color="white")))
    )
    
    # Force axes labels to white
    fig.update_xaxes(tickfont=dict(color="white"), title_font=dict(color="white"))
    fig.update_yaxes(tickfont=dict(color="white"), title_font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # C. Insights Section
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.subheader("💡 Sustainability Insights")
    st.write(ai_response)
    
    st.download_button(
        label="📥 Download Full Report",
        data=ai_response,
        file_name="Intelliwaste_Sustainability_Report.txt",
        mime="text/plain"
    )
    st.markdown('</div>', unsafe_allow_html=True)