"""
utils/history.py
Session-based scan history tracker (in-memory, no database needed).
"""

from datetime import datetime

def create_history():
    """Returns a fresh empty history list."""
    return []

def add_entry(history: list, item_name: str, category: str, bin_color: str) -> list:
    """Add a new scan to history."""
    history.append({
        "item": item_name,
        "category": category,
        "bin": bin_color,
        "time": datetime.now().strftime("%H:%M")
    })
    return history

def format_history(history: list) -> str:
    """Format history for display in UI."""
    if not history:
        return "No items scanned yet."
    lines = [f"**{i+1}. {e['item']}** — {e['category']} → {e['bin']} bin  _{e['time']}_"
             for i, e in enumerate(reversed(history))]
    return "\n".join(lines)

def get_stats(history: list) -> str:
    """Return a simple summary of scanned items."""
    if not history:
        return ""
    total = len(history)
    cats = {}
    for e in history:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    top = max(cats, key=cats.get)
    return f"✅ {total} items scanned this session | Most common: **{top}**"