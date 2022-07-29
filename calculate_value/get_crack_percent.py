def get_crack_percent(items):
    crack_longitudinal_low = 0
    crack_longitudinal_med = 0
    crack_longitudinal_high = 0
    crack_transverse_low = 0
    crack_transverse_med = 0
    crack_transverse_high = 0
    crack_cold_joint_low = 0
    crack_cold_joint_med = 0
    crack_cold_joint_high = 0
    crack_fatigue_low = 0
    crack_fatigue_med = 0
    crack_fatigue_high = 0
    patching_low = 0
    patching_med = 0
    patching_high = 0
    pothole_low = 0
    pothole_med = 0
    pothole_high = 0
    rutting = 0
    iri = 0
    area = 0
    for item in items:
        crack = item["crack"]
        longitudinal = crack["longitudinal"]
        crack_longitudinal_low += float(longitudinal["low"])
        crack_longitudinal_med += float(longitudinal["med"])
        crack_longitudinal_high += float(longitudinal["high"])
        transverse = crack["transverse"]
        crack_transverse_low += float(transverse["low"])
        crack_transverse_med += float(transverse["med"])
        crack_transverse_high += float(transverse["high"])
        cold_joint = crack["cold_joint"]
        crack_cold_joint_low += float(cold_joint["low"])
        crack_cold_joint_med += float(cold_joint["med"])
        crack_cold_joint_high += float(cold_joint["high"])
        fatigue = crack["fatigue"]
        crack_fatigue_low += float(fatigue["low"])
        crack_fatigue_med += float(fatigue["med"])
        crack_fatigue_high += float(fatigue["high"])
        patching = crack["patching"]
        patching_low += float(patching["low"])
        patching_med += float(patching["med"])
        patching_high += float(patching["high"])
        pothole = crack["pothole"]
        pothole_low += float(pothole["low"])
        pothole_med += float(pothole["med"])
        pothole_high += float(pothole["high"])
        score = item["score"]
        rutting = float(score["rutting"])
        iri = float(score["iri"])
        area += float(item["width"]) * 10
    return ((crack_longitudinal_low + crack_longitudinal_med + crack_longitudinal_high + 
             crack_transverse_low + crack_transverse_med + crack_transverse_high + 
             crack_cold_joint_low + crack_cold_joint_med + crack_cold_joint_high) * 0.3 + 
            crack_fatigue_low + crack_fatigue_med + crack_fatigue_high + 
            patching_low + patching_med + patching_high + 
            pothole_low + pothole_med + pothole_high) / area * 100,\
            rutting / len(items), \
            iri / len(items), \
            area
#    return ((crack_longitudinal_low + crack_longitudinal_med + crack_longitudinal_high + crack_transverse_low + crack_transverse_med + crack_transverse_high + crack_cold_joint_low + crack_cold_joint_med + crack_cold_joint_high) * 0.3 + crack_fatigue_low + crack_fatigue_med + crack_fatigue_high + patching_low + patching_med + patching_high + pothole_low + pothole_med + pothole_high) / area * 100, rutting / len(items), iri / len(items), area
