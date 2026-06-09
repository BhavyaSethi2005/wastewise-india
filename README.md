---
title: WasteWise India
emoji: 🗑️
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.29.0
app_file: app.py
pinned: false
license: mit
---

# 🗑️ WasteWise India

Photo any waste item → know exactly which bin it goes in and why.

India generates 159,000 tonnes of waste daily. Citizens know green vs blue bin basics
but consistently fail on unusual items — medicine strips, agarbatti ash, thermocol,
paan wrappers, CFL bulbs, old batteries.

## What it does
- 📸 Upload any waste item photo → instant bin guidance
- 🏙️ City-specific rules for 19 Indian cities
- 🌍 National SWM Rules 2026 fallback for all other cities and villages
- 🇮🇳 Hindi language support
- 📋 Session scan history with stats

## Accuracy
- 100% category accuracy on 25-item structured test set
- 100% bin accuracy on 25-item structured test set

## Tech Stack
- Gemini 3.1 Flash Lite · LangChain RAG · FAISS · all-MiniLM-L6-v2 · Gradio