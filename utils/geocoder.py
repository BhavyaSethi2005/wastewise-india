"""
utils/geocoder.py
Reverse geocoding — converts lat/lng to nearest supported city.
Uses OpenStreetMap Nominatim API (free, no key needed) for city name.
If exact name match fails, falls back to nearest supported city by distance.
"""

import requests
from math import radians, sin, cos, sqrt, atan2
from utils.city_rules import SUPPORTED_CITIES

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "WasteWiseIndia/1.0 (waste classification app)"}

# Map common city name variations to our exact supported city names
CITY_NAME_MAP = {
    "indore":       "Indore",
    "new delhi":    "Delhi",
    "delhi":        "Delhi",
    "mumbai":       "Mumbai",
    "bombay":       "Mumbai",
    "bangalore":    "Bengaluru",
    "bengaluru":    "Bengaluru",
    "bengalore":    "Bengaluru",
    "pune":         "Pune",
    "hyderabad":    "Hyderabad",
    "chennai":      "Chennai",
    "madras":       "Chennai",
    "kolkata":      "Kolkata",
    "calcutta":     "Kolkata",
    "ahmedabad":    "Ahmedabad",
    "jaipur":       "Jaipur",
    "lucknow":      "Lucknow",
    "surat":        "Surat",
    "kochi":        "Kochi",
    "cochin":       "Kochi",
    "chandigarh":   "Chandigarh",
    "nagpur":       "Nagpur",
    "bhopal":       "Bhopal",
    "patna":        "Patna",
    "vadodara":     "Vadodara",
    "baroda":       "Vadodara",
    "coimbatore":   "Coimbatore",
}

# Approximate lat/lng of each supported city — used for nearest-city fallback
CITY_COORDS = {
    "Indore":     (22.7196, 75.8577),
    "Delhi":      (28.7041, 77.1025),
    "Mumbai":     (19.0760, 72.8777),
    "Bengaluru":  (12.9716, 77.5946),
    "Pune":       (18.5204, 73.8567),
    "Hyderabad":  (17.3850, 78.4867),
    "Chennai":    (13.0827, 80.2707),
    "Kolkata":    (22.5726, 88.3639),
    "Ahmedabad":  (23.0225, 72.5714),
    "Jaipur":     (26.9124, 75.7873),
    "Lucknow":    (26.8467, 80.9462),
    "Surat":      (21.1702, 72.8311),
    "Kochi":      (9.9312, 76.2673),
    "Chandigarh": (30.7333, 76.7794),
    "Nagpur":     (21.1458, 79.0882),
    "Bhopal":     (23.2599, 77.4126),
    "Patna":      (25.5941, 85.1376),
    "Vadodara":   (22.3072, 73.1812),
    "Coimbatore": (11.0168, 76.9558),
}


def _distance_km(lat1, lng1, lat2, lng2) -> float:
    """Haversine distance between two lat/lng points in km."""
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def _nearest_city(lat: float, lng: float) -> tuple[str, float]:
    """Returns (nearest_city_name, distance_km) from our supported cities."""
    nearest_city = None
    nearest_dist = float("inf")

    for city, (city_lat, city_lng) in CITY_COORDS.items():
        dist = _distance_km(lat, lng, city_lat, city_lng)
        if dist < nearest_dist:
            nearest_dist = dist
            nearest_city = city

    return nearest_city, nearest_dist


def coords_to_city(lat: float, lng: float) -> dict:
    """
    Convert GPS coordinates to supported city.

    Returns dict:
        - city: matched or nearest supported city name
        - exact_match: True if city name matched directly
        - distance_km: distance to nearest city (only if not exact match)
        - detected_name: raw city/town name from GPS (for display)
    """
    detected_name = ""

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={"lat": lat, "lon": lng, "format": "json", "addressdetails": 1},
            headers=HEADERS,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})

        raw_city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("county") or
            ""
        )
        detected_name = raw_city
        raw_city_lower = raw_city.lower().strip()

        # Try exact match first
        matched = CITY_NAME_MAP.get(raw_city_lower)
        if matched and matched in SUPPORTED_CITIES:
            return {"city": matched, "exact_match": True, "distance_km": 0, "detected_name": detected_name}

        # Try partial match
        for key, value in CITY_NAME_MAP.items():
            if key in raw_city_lower:
                return {"city": value, "exact_match": True, "distance_km": 0, "detected_name": detected_name}

    except Exception:
        pass  # fall through to nearest-city by coordinates

    # No exact match — find nearest supported city by distance
    nearest_city, dist = _nearest_city(lat, lng)
    return {
        "city": nearest_city,
        "exact_match": False,
        "distance_km": round(dist, 1),
        "detected_name": detected_name
    }