# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 21:32:23 2026

@author: cassi
"""

"""
RTT vs. Speed-of-Light
Networks Assignment — Measurement & Geography

Run with: python rtt_speedoflight.py   (no sudo needed)
Requires: pip install requests matplotlib numpy
"""

import math, time, os, requests, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import urllib.request
from matplotlib.lines import Line2D


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

TARGETS = {
    "Tokyo":        {"url": "http://www.google.co.jp",   "coords": (35.6762,  139.6503), "continent": "Asia"},
    "São Paulo":    {"url": "http://www.google.com.br",  "coords": (-23.5505, -46.6333), "continent": "S. America"},
    "Lagos":        {"url": "http://www.google.com.ng",  "coords": (6.5244,     3.3792), "continent": "Africa"},
    "Frankfurt":    {"url": "http://www.google.de",      "coords": (50.1109,    8.6821), "continent": "Europe"},
    "Sydney":       {"url": "http://www.google.com.au",  "coords": (-33.8688, 151.2093), "continent": "Oceania"},
    "Mumbai":       {"url": "http://www.google.co.in",   "coords": (19.0760,   72.8777), "continent": "Asia"},
    "London":       {"url": "http://www.google.co.uk",   "coords": (51.5074,   -0.1278), "continent": "Europe"},
    "Singapore":    {"url": "http://www.google.com.sg",  "coords": (1.3521,   103.8198), "continent": "Asia"},
    
    #Additional URLs
    "Sendai":       {"url": "http://www.tohoku.ac.jp",   "coords": (38.2682,  140.8694), "continent": "Asia"},
    "Seoul":        {"url": "http://www.snu.ac.kr",      "coords": (37.4600,  126.9520), "continent": "Asia"},
    "New Delhi":    {"url": "http://www.iitd.ac.in",     "coords": (28.5450,   77.1926), "continent": "Asia"},
    "Santiago":     {"url": "http://www.uchile.cl",      "coords": (-33.4569, -70.6483), "continent": "S. America"},
    "Johannesburg": {"url": "http://www.wits.ac.za",     "coords": (-26.1929,  28.0305), "continent": "Africa"},
    "Berlin":       {"url": "http://www.fu-berlin.de",   "coords": (52.4537,   13.2897), "continent": "Europe"},
    "London-IC":    {"url": "http://www.imperial.ac.uk", "coords": (51.4988,   -0.1749), "continent": "Europe"},
    "Canberra":     {"url": "http://www.anu.edu.au",     "coords": (-35.2777,  149.1185), "continent": "Oceania"},
}

PROBES           = 15
FIBER_SPEED_KM_S = 200_000
FIGURES_DIR      = "figures"

CONTINENT_COLORS = {
    "Asia":      "#e63946",
    "S. America":"#2a9d8f",
    "Africa":    "#e9c46a",
    "Europe":    "#457b9d",
    "Oceania":   "#a8dadc",
}

# ─────────────────────────────────────────────
# TASK 1 — MEASURE RTTs
# ─────────────────────────────────────────────

#Measure RTT to `url` using HTTP requests.
def measure_rtt(url: str, probes: int = PROBES) -> dict:

    samples = []
    lost    = 0

    #Send 15 HTTP request (loop 'probes' times)
    for _ in range(probes):
  
        try:
            # start time
            start = time.perf_counter()
            
            #send HTTP request
            urllib.request.urlopen(url, timeout=3)
            
            #Elapsed time in ms
            elapsed_ms = (time.perf_counter() - start) * 1000
            
            #Save sample in list
            samples.append(elapsed_ms)
         
        #On any exception, count as lost
        except Exception:
            lost += 1
        
        #Sleep 0.2s between probes
        time.sleep(0.2)

    #If all probes lost, return None for all stats
    if not samples:
        return {"min_ms": None, "mean_ms": None, "median_ms": None,
                "loss_pct": 100.0, "samples": []}
    
    # Computing loss_pct
    loss_pct = (lost / probes) * 100


    # TODO: compute and return stats
    return {
        #Compute min, mean, median using numpy
        "min_ms":    float(np.min(samples)),
        "mean_ms":   float(np.mean(samples)),
        "median_ms": float(np.median(samples)),
        "loss_pct":  loss_pct,
        "samples":   samples,
        }  


# ─────────────────────────────────────────────
# TASK 2 — HAVERSINE + INEFFICIENCY
# ─────────────────────────────────────────────

def great_circle_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance in km using the Haversine formula.

    Haversine:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1−a))
        d = R * c       where R = 6371 km

    TODO: implement from scratch. Use math.radians() to convert degrees.
    Do NOT use geopy or any distance library.
    """
    
    #Radius of earth (km)
    R = 6371
    
    # Convert latitude and longitude values from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Difference in lat and difference in lon
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Great-circle distance:
    d = R * c
    return d
    
    

def get_my_location() -> tuple[float, float, str]:
    """Return (lat, lon, city) for this machine's public IP."""
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5).json()
        lat, lon = map(float, r["loc"].split(","))
        return lat, lon, r.get("city", "Your Location")
    except Exception:
        print("Could not auto-detect location. Defaulting to Boston.")
        return 42.3601, -71.0589, "Boston"




def compute_inefficiency(results: dict, src_lat: float, src_lon: float) -> dict:
   
    
    #Annotate each city in resultswith "distance_km," "theoretical_min_ms," "inefficiency_ratio," "high_inefficiency"
    for city, data in results.items():
        # unpack destination coordinates
        city_lat, city_lon = data["coords"]

        # "distance_km:" great-circle distance from source
        #For each city, call great_circle_km()
        distance_km = great_circle_km(src_lat, src_lon, city_lat, city_lon)

        # compute theoretical_min_ms (*2 for roundtrip, *1000 for ms)
        theoretical_min_ms = (distance_km / 200000) * 2 * 1000

        # Compute ratio. If median_ms is None, set ratio to None
        if data["median_ms"] is None:
            ratio = None
            high_inefficiency = False
        else:
            ratio = data["median_ms"] / theoretical_min_ms
            high_inefficiency = ratio > 3.0

        # Add to results dictionary
        data["distance_km"] = distance_km
        data["theoretical_min_ms"] = theoretical_min_ms
        data["inefficiency_ratio"] = ratio
        data["high_inefficiency"] = high_inefficiency

    return results


# ─────────────────────────────────────────────
# TASK 3 — PLOTS
# ─────────────────────────────────────────────

def make_plots(results: dict):
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    valid = {c: d for c, d in results.items() if d.get("median_ms") is not None}
    cities = sorted(valid, key=lambda c: valid[c]["distance_km"])

    '''
    Figure 1 — fig1_rtt_comparison.png
        Grouped bar chart: measured median RTT vs. theoretical min RTT per city.
        Sort cities by distance_km ascending.
        Label axes, add legend and title.
    '''

    # ── Figure 1 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 6))

    # x positions
    x = np.arange(len(cities))
    width = 0.35

    # median and theoretical values
    median = [valid[c]["median_ms"] for c in cities]
    theoretical = [valid[c]["theoretical_min_ms"] for c in cities]

    # grouped bars
    ax.bar(x - width / 2, median, width, label="Measured Median RTT")
    ax.bar(x + width / 2, theoretical, width, label="Theoretical Min RTT")

    # labels
    ax.set_xlabel("City")
    ax.set_ylabel("RTT (ms)")
    ax.set_title("Measured Median RTT vs. Theoretical Minimum RTT")
    ax.set_xticks(x)
    ax.set_xticklabels(cities, rotation=45, ha="right")
    ax.legend()

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig1_rtt_comparison.png", dpi=150, bbox_inches="tight")
    
    plt.show

    plt.close()


    '''
    Figure 2 — fig2_distance_scatter.png
        Scatter: x = distance_km, y = measured median RTT.
        Draw a dashed line for theoretical minimum.
        Label each point with city name.
        Color by continent using CONTINENT_COLORS.
        Add continent legend and title.
    '''

    # ── Figure 2 ──────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 7))

    # scatter points
    for city in cities:
        d = valid[city]
        color = CONTINENT_COLORS.get(d["continent"], "#888888")

        ax.scatter(d["distance_km"], d["median_ms"], color=color, s=80, zorder=3)

        ax.annotate(
            city,
            (d["distance_km"], d["median_ms"]),
            textcoords="offset points",
            xytext=(6, 4),
            fontsize=8
        )

    # dashed theoretical minimum line
    dist_range = np.linspace(0, max(d["distance_km"] for d in valid.values()), 200)
    theor_line = 2 * (dist_range / FIBER_SPEED_KM_S) * 1000
    ax.plot(dist_range, theor_line, "k--", label="Theoretical Min RTT", linewidth=1.2)

    # legend
    legend_handles = [mpatches.Patch(color=c, label=k) for k, c in CONTINENT_COLORS.items()]
    legend_handles.append(Line2D([0], [0], color="black", linestyle="--", label="Theoretical Min RTT"))

    ax.legend(handles=legend_handles, fontsize=8)
    ax.set_xlabel("Great-Circle Distance (km)")
    ax.set_ylabel("Measured Median RTT (ms)")
    ax.set_title("Distance Vs. Measured RTT")

    plt.tight_layout()
    plt.savefig(f"{FIGURES_DIR}/fig2_distance_scatter.png", dpi=150, bbox_inches="tight")
    
    plt.show

    
    plt.close()

    print(f"Figures saved to {FIGURES_DIR}/")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    src_lat, src_lon, src_city = get_my_location()
    print(f"Your location: {src_city} ({src_lat:.4f}, {src_lon:.4f})\n")

    results = {}
    for city, info in TARGETS.items():
        print(f"Probing {city} ({info['url']}) ...", end=" ", flush=True)
        stats = measure_rtt(info["url"])
        results[city] = {**stats, "coords": info["coords"], "continent": info["continent"]}
        med = stats.get("median_ms")
        print(f"median={med:.1f} ms  loss={stats['loss_pct']:.0f}%" if med else "unreachable")

    results = compute_inefficiency(results, src_lat, src_lon)

    print(f"\n{'City':<14} {'Dist km':>8} {'Median ms':>10} {'Theor. ms':>10} {'Ratio':>7}")
    print("─" * 55)
    for city, d in sorted(results.items(), key=lambda x: x[1].get("distance_km", 0)):
        dist  = d.get("distance_km", 0)
        med   = d.get("median_ms")
        theor = d.get("theoretical_min_ms")
        ratio = d.get("inefficiency_ratio")
        flag  = " ⚠️" if d.get("high_inefficiency") else ""
        print(f"{city:<14} {dist:>8.0f} "
              f"{(f'{med:.1f}' if med else 'N/A'):>10} "
              f"{(f'{theor:.1f}' if theor else 'N/A'):>10} "
              f"{(f'{ratio:.2f}' if ratio else 'N/A'):>7}{flag}")

    make_plots(results)

if __name__ == "__main__":
    main()
