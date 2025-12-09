# app.py

import streamlit as st
import plotly.graph_objects as go
import os
from fitness_scoring import *

# Helper to round numeric values to nearest integer for display
def round_int(value):
    try:
        return int(round(float(value)))
    except Exception:
        return value

st.set_page_config(page_title="DESCEND Fitness Dashboard", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #2a2a2a;
        color: #ffffff;
    }
    h1, h2, h3, h4 {
        color: #ff8c00;
        font-family: 'Arial Black', sans-serif;
    }
    .stAlert {
        background-color: #1a1a1a;
    }
    .metric-card {
        background-color: #3a3a3a;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff8c00;
    }
    </style>
""", unsafe_allow_html=True)

# Header with banner
banner_path = "descend banner2.png"
try:
    if os.path.exists(banner_path):
        col_banner1, col_banner2, col_banner3 = st.columns([1, 3, 1])
        with col_banner2:
            st.image(banner_path, use_container_width=True)
    else:
        st.markdown("### 🏔️ DESCEND")
        st.markdown("**GRAVITY CONDITIONING**")
except Exception:
    st.markdown("### 🏔️ DESCEND")
    st.markdown("**GRAVITY CONDITIONING**")

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    with st.form("fitness_form"):
        st.subheader("Test Data Input")
        
        # Athlete Profile
        st.markdown("#### Athlete Profile")
        test_date = st.date_input("Test Date")
        sex = st.selectbox("Sex", ["male", "female"])
        age = st.number_input("Age", min_value=10, max_value=100, value=38)
        bodyweight = st.number_input("Bodyweight (kg)", min_value=30.0, value=85.0)
        discipline = st.selectbox("Discipline", ["dh", "edr"])
        
        st.markdown("---")
        
        # Test Results 
        st.markdown("#### Strength Tests")
        trap_bar_3rm = st.number_input("TrapBar 3RM (kg)", min_value=0.0, value=180.0)
        split_squat_5rm = st.number_input("Split Squat 5RM (kg)", min_value=0.0, value=60.0)
        
        st.markdown("#### Power Tests")
        broad_jump = st.number_input("Broad Jump (cm)", min_value=0.0, value=230.0)
        med_ball_toss = st.number_input("Med Ball Toss (m)", min_value=0.0, value=8.0)
        
        st.markdown("#### Conditioning Tests")
        bike_12min = st.number_input("12 min Bike (avg Watts)", min_value=0.0, value=250.0)
        row_meters = st.number_input("3 min Row (Metres)", min_value=0.0, value=700.0)
        assault_bike = st.number_input("60s Assault Bike (cal)", min_value=0.0, value=35.0)
        bike_peak_watts = st.number_input("6s Sprint (Peak Watts)", min_value=0.0, value=1100.0)

        submitted = st.form_submit_button("🔄 Calculate Scores", use_container_width=True)

with col2:
    if submitted:
        # Calculate scores using the functions (all return 0-100 scale)
        strength = compute_strength_score(trap_bar_3rm, bodyweight)
        endurance = compute_strength_endurance_score(split_squat_5rm, bodyweight)
        power = compute_power_score(broad_jump, med_ball_toss, sex)
        aerobic = compute_aerobic_score(bike_12min)
        anaerobic = compute_anaerobic_score(row_meters, assault_bike, bike_peak_watts, sex)
        
        # Compute overall as mean of all test scores
        test_scores_dict = {
            "strength": strength,
            "endurance": endurance,
            "power": power,
            "aerobic": aerobic,
            "anaerobic": anaerobic
        }
        overall = compute_overall_score(test_scores_dict)
        
        # For program recommendation, convert to 0-10 scale
        overall_for_program = overall / 10
        program = recommend_program(overall_for_program, discipline)
        
        # Results header
        st.markdown("## MTB Athlete Profile – Strength | Endurance | Anaerobic | Aerobic | Power")
        
        # Horizontal bar chart
        categories = [
            "POWER SCORE",
            "AEROBIC SCORE", 
            "ANAEROBIC SCORE",
            "STRENGTH ENDURANCE SCORE",
            "ABSOLUTE STRENGTH SCORE"
        ]
        
        values = [power, aerobic, anaerobic, endurance, strength]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=categories,
            x=values,
            orientation='h',
            marker=dict(
                color='#ff8c00',
                line=dict(color='#ff6600', width=1)
            ),
            text=[f"{round_int(v)}" for v in values],
            textposition='outside',
            textfont=dict(color='#ff8c00', size=14, family='Arial Black')
        ))
        
        fig.update_layout(
            plot_bgcolor='#2a2a2a',
            paper_bgcolor='#2a2a2a',
            font=dict(color='#ffffff', size=12, family='Arial'),
            xaxis=dict(
                range=[0, 120],
                showgrid=True,
                gridcolor='#404040',
                zeroline=True,
                zerolinecolor='#404040',
                tickvals=[0, 20, 40, 60, 80, 100],
                tickfont=dict(color='#999999')
            ),
            yaxis=dict(
                showgrid=False,
                tickfont=dict(color='#ffffff', size=11)
            ),
            height=350,
            margin=dict(l=200, r=50, t=20, b=40),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Overall score and recommendation
        st.markdown("---")
        
        score_col, prog_col = st.columns(2)
        
        with score_col:
            st.markdown(f"### OVERALL SCORE: <span style='color: #ff8c00; font-size: 48px;'>{round_int(overall)}</span>", 
                       unsafe_allow_html=True)
        
        with prog_col:
            st.markdown(f"### RECOMMENDED PROGRAM: <span style='color: #ff8c00; font-size: 32px;'>{program}</span>", 
                       unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed score breakdown
        st.subheader("📊 Detailed Score Breakdown")
        
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        
        with metric_col1:
            st.metric("Absolute Strength", f"{round_int(strength)}")
            st.metric("Strength Endurance", f"{round_int(endurance)}")
        
        with metric_col2:
            st.metric("Power", f"{round_int(power)}")
            st.metric("Aerobic", f"{round_int(aerobic)}")
        
        with metric_col3:
            st.metric("Anaerobic", f"{round_int(anaerobic)}")
            st.metric("Overall", f"{round_int(overall)}")
        
        # Test performance summary
        st.markdown("---")
        st.subheader("📋 Test Performance Summary")
        
        elite_standards = get_elite_standards(bodyweight, sex)
        
        # Individual test scores with performance bands
        test_scores = {
            "trap_bar": strength,
            "split_squat": endurance,
            "broad_jump": (broad_jump / elite_standards['broad_jump']) * 80,
            "med_ball": (med_ball_toss / elite_standards['med_ball']) * 80,
            "bike_12min": aerobic,
            "rower_3min": (row_meters / elite_standards['rower_3min']) * 100,
            "airbike_60s": (assault_bike / elite_standards['airbike_60s']) * 80,
            "sprint_6s": (bike_peak_watts / elite_standards['sprint_6s']) * 80,
        }
        
        # Clamp all scores to 100 max
        test_scores = {k: min(v, 100) for k, v in test_scores.items()}
        
        # Get performance bands
        test_bands = {k: score_to_band(v) for k, v in test_scores.items()}
        
        summary_data = {
            "Test": [
                "Trap Bar 3RM", 
                "Split Squat 5RM", 
                "Broad Jump",
                "Med Ball Toss",
                "12min Bike (avg)", 
                "Rower 3min", 
                "Assault Bike 60s", 
                "Sprint 6s Peak"
            ],
            "Result": [
                f"{round_int(trap_bar_3rm)}kg", 
                f"{round_int(split_squat_5rm)}kg", 
                f"{round_int(broad_jump)}cm",
                f"{round_int(med_ball_toss)}m",
                f"{round_int(bike_12min)}W", 
                f"{round_int(row_meters)}m", 
                f"{round_int(assault_bike)} cal", 
                f"{round_int(bike_peak_watts)}W"
            ],
            "Elite Target": [
                f"{round_int(elite_standards['trap_bar'])}kg",
                f"{round_int(elite_standards['split_squat'])}kg",
                f"{round_int(elite_standards['broad_jump'])}cm",
                f"{elite_standards['med_ball']:.1f}m",
                f"{round_int(elite_standards['bike_12min'])}W",
                f"{round_int(elite_standards['rower_3min'])}m",
                f"{round_int(elite_standards['airbike_60s'])} cal",
                f"{round_int(elite_standards['sprint_6s'])}W"
            ],
            "Score": [
                f"{round_int(test_scores['trap_bar'])}",
                f"{round_int(test_scores['split_squat'])}",
                f"{round_int(test_scores['broad_jump'])}",
                f"{round_int(test_scores['med_ball'])}",
                f"{round_int(test_scores['bike_12min'])}",
                f"{round_int(test_scores['rower_3min'])}",
                f"{round_int(test_scores['airbike_60s'])}",
                f"{round_int(test_scores['sprint_6s'])}"
            ],
            "Performance": [
                test_bands['trap_bar'],
                test_bands['split_squat'],
                test_bands['broad_jump'],
                test_bands['med_ball'],
                test_bands['bike_12min'],
                test_bands['rower_3min'],
                test_bands['airbike_60s'],
                test_bands['sprint_6s']
            ]
        }
        
        import pandas as pd
        df = pd.DataFrame(summary_data)
        
        # Style the dataframe with color-coded performance bands
        def highlight_performance(row):
            band_color = get_band_color(row['Performance'])
            return ['', '', '', '', f'background-color: {band_color}; color: black; font-weight: bold']
        
        styled_df = df.style.apply(highlight_performance, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Performance band legend
        st.markdown("---")
        st.markdown("#### Performance Band Guide")
        legend_col1, legend_col2, legend_col3, legend_col4 = st.columns(4)
        
        with legend_col1:
            st.markdown("🥇 **Elite**: ≥80")
        with legend_col2:
            st.markdown("🥈 **Great**: 55-79")
        with legend_col3:
            st.markdown("🥉 **Good**: 45-54")
        with legend_col4:
            st.markdown("🔴 **Not Great**: <45")

    else:
        # Welcome screen
        st.markdown("## 👈 Enter Test Data to Generate Profile")
        st.markdown("---")
        st.markdown("""
        ### About the DESCEND Testing Protocol
        
        This comprehensive fitness assessment evaluates MTB athletes across **5 key performance domains**:
        
        #### 🏋️ Absolute Strength
        - Trap bar deadlift 3RM relative to bodyweight
        - Elite: 2.0x bodyweight (80 points)
        
        #### 💪 Strength Endurance  
        - Split squat 5RM capacity per leg
        - Elite: ~0.75x bodyweight (80 points)
        
        #### ⚡ Power
        - Broad jump + med ball toss
        - Elite: 260cm (M) / 200cm (F) broad jump, 11m (M) / 8m (F) med ball
        
        #### 🫁 Aerobic Capacity
        - 12-minute sustained bike effort
        - Elite: 350W average (80 points)
        
        #### 🔥 Anaerobic Capacity
        - Short-duration high-intensity tests
        - Elite: 45 cal airbike, 900m rower, 1300W sprint
        
        ---
        
        **Scoring System:**
        - Each test: 0-100 points
        - Overall: average of all test scores
        - Elite threshold: 80 points
        
        **Program Recommendations:**
        - Overall < 10: Foundation program (DH3/Enduro3)
        - Overall ≥ 10: Performance program (DH2/Enduro2)
        """)
        
        st.info("💡 **Tip:** Fill in the form on the left and click 'Calculate Scores' to see your athlete profile.")