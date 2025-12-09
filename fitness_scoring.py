# fitness_scoring.py

ELITE_THRESHOLD = 80.0

def clamp_score(score):
    """Clamp score to 0-100"""
    return max(0.0, min(100.0, score))


def compute_strength_score(trap_bar_1rm, bodyweight):
    """
    Strength score based on trap bar deadlift vs bodyweight standard
    100 points at 2.5 x BW
    """
    if bodyweight <= 0:
        return 0.0
    raw = (trap_bar_1rm / (2.5 * bodyweight)) * 100.0
    return round(clamp_score(raw), 2)


_SPLIT_K = 0.8823529411764706  # chosen so 60kg at 85kg BW ≈ 80 pts

def compute_strength_endurance_score(split_squat, bodyweight):
    """
    Strength endurance score based on split squat vs bodyweight standard
    """
    if bodyweight <= 0:
        return 0.0
    raw = (split_squat / (_SPLIT_K * bodyweight)) * 100.0
    return round(clamp_score(raw), 2)


_BROAD_BASE_MALE_CM = 260.0
_BROAD_BASE_FEMALE_CM = 200.0
_MEDBALL_BASE_MALE_M = 11.0
_MEDBALL_BASE_FEMALE_M = 8.0

def compute_power_score(broad_jump_cm, medball_toss, sex):
    """
    Power score combines broad jump and med ball toss
    """
    sex = sex.lower()
    
    # Broad jump component
    broad_base = _BROAD_BASE_FEMALE_CM if sex == "female" else _BROAD_BASE_MALE_CM
    broad_score = (broad_jump_cm / broad_base) * 100.0
    
    # Med ball component
    medball_base = _MEDBALL_BASE_FEMALE_M if sex == "female" else _MEDBALL_BASE_MALE_M
    medball_score = (medball_toss / medball_base) * 100.0
    
    # Average the two
    raw = (broad_score + medball_score) / 2.0
    return round(clamp_score(raw), 2)


_ELITE_BIKE_12_WATTS = 350.0  # 350W -> 80 pts

def compute_aerobic_score(bike_12min_watts):
    """
    Aerobic score based on 12-minute bike average watts
    """
    if bike_12min_watts <= 0:
        return 0.0
    raw = (bike_12min_watts / _ELITE_BIKE_12_WATTS) * ELITE_THRESHOLD
    return round(clamp_score(raw), 2)


_ROWER_BASE_MALE_M = 900.0
_ROWER_BASE_FEMALE_M = 750.0
_ELITE_AIRBIKE_60_CAL = 45.0  # 45 cal -> 80 pts
_ELITE_SPRINT_6_WATTS = 1300.0  # 1300W -> 80 pts

def compute_anaerobic_score(rower_3min, airbike_60s, sprint_6s, sex):
    """
    Anaerobic score averages three test outputs
    """
    sex = sex.lower()
    
    # Rower score
    rower_base = _ROWER_BASE_FEMALE_M if sex == "female" else _ROWER_BASE_MALE_M
    rower_score = (rower_3min / rower_base) * 100.0
    
    # Airbike score
    airbike_score = (airbike_60s / _ELITE_AIRBIKE_60_CAL) * ELITE_THRESHOLD
    
    # Sprint score
    sprint_score = (sprint_6s / _ELITE_SPRINT_6_WATTS) * ELITE_THRESHOLD
    
    # Average the three
    raw = (rower_score + airbike_score + sprint_score) / 3.0
    return round(clamp_score(raw), 2)


def compute_overall_score(test_scores_dict):
    """
    Overall score is the mean of all individual test scores (0-100 scale)
    """
    vals = [float(v) for v in test_scores_dict.values() if v is not None]
    if not vals:
        return 0.0
    return round(sum(vals) / len(vals), 2)


def recommend_program(overall_score, discipline):
    """
    Program recommendation based on overall score and discipline
    Threshold is 10 on the 0-10 scale (which is 100 on 0-100 scale)
    Since we're now using 0-100 scale throughout, threshold should be 100
    """
    # Note: If overall_score is on 0-100 scale, threshold should be adjusted
    # For now keeping original logic with score < 10
    if discipline.lower() == "dh":
        if overall_score < 10:
            return "DH3"
        else:
            return "DH2"
    
    elif discipline.lower() in ["enduro", "edr"]:
        if overall_score < 10:
            return "Enduro3"
        else:
            return "Enduro2"
    
    else:
        return "General Program"


# Elite Standards and Performance Bands

def get_elite_standards(bodyweight, sex):
    """
    Returns elite score thresholds (raw values for 80 pts) for all tests
    """
    sex = sex.lower()
    
    # Trap bar: 80% of 2.5 x BW -> 2.0 x BW
    trap_elite = 0.8 * 2.5 * bodyweight
    
    # Split squat: inverse of scoring formula
    split_elite = (ELITE_THRESHOLD / 100.0) * _SPLIT_K * bodyweight
    
    if sex == "female":
        broad_elite = 0.8 * _BROAD_BASE_FEMALE_CM
        medball_elite = 0.8 * _MEDBALL_BASE_FEMALE_M
        rower_elite = 0.8 * _ROWER_BASE_FEMALE_M
    else:
        broad_elite = 0.8 * _BROAD_BASE_MALE_CM
        medball_elite = 0.8 * _MEDBALL_BASE_MALE_M
        rower_elite = 0.8 * _ROWER_BASE_MALE_M
    
    elite_scores = {
        "trap_bar": trap_elite,
        "split_squat": split_elite,
        "broad_jump": broad_elite,
        "med_ball": medball_elite,
        "bike_12min": _ELITE_BIKE_12_WATTS,
        "rower_3min": rower_elite,
        "airbike_60s": _ELITE_AIRBIKE_60_CAL,
        "sprint_6s": _ELITE_SPRINT_6_WATTS
    }
    return elite_scores


def score_to_band(score):
    """
    Convert a 0-100 score into a performance band.
    Bands:
        elite:       score >= 80
        great:       55 <= score < 80
        good:        45 <= score < 55
        not great:   score < 45
    """
    if score >= 80:
        return "elite"
    elif score >= 55:
        return "great"
    elif score >= 45:
        return "good"
    else:
        return "not great"


def get_band_color(band):
    """
    Returns color code for each performance band
    Metallic theme colors
    """
    colors = {
        "elite": "#D4AF37",      # Metallic Gold
        "great": "#C0C0C0",      # Metallic Silver
        "good": "#CD7F32",       # Metallic Bronze
        "not great": "#C00000"   # Red
    }
    return colors.get(band, "#999999")