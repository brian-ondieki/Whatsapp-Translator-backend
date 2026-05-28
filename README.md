# 🚀 WhatsApp Live Translator Extension

A high-performance, privacy-focused Chrome Extension that automatically detects and translates non-English WhatsApp Web messages inline. Backed by a live FastAPI server hosted on Render, featuring advanced UX controls and robust network error-handling pipelines.

---

## ✨ Features

*   **⚡ Live Cloud Translation:** Zero local setup needed. Powered by a live FastAPI instance deployed globally on Render.
*   **🛠️ Robust Network Resiliency:** Equipped with an Automated Retry Logic and Exponential Backoff handler to gracefully withstand server sleep/wake cold starts on the Render Free Tier.
*   **🧠 Intelligent Language Fallback:** Features dual-pass language verification. Uses `langdetect` for structured text and automatically falls back to `deep-translator`'s internal engine for short phrases, slang, or emojis.
*   **🎨 Advanced Inline UX:**
    *   **Hide/Show Toggle:** Instantly minimize translated text blocks to reduce screen clutter.
    *   **One-Click Copy:** Copy translated text instantly to your clipboard with immediate UI state feedback.
    *   **Theme-Adaptive Styling:** Modern dark/light adaptive backgrounds seamlessly matching native WhatsApp layouts.
*   **🔒 Granular Permissions:** Strictly bounded to `web.whatsapp.com` and your dedicated backend URL.

---

## 🏗️ Architecture

```text
┌────────────────────────┐         HTTPS          ┌────────────────────────┐
│  Chrome Content Script │ ─────────────────────> │ FastAPI Backend Server │
│  (WhatsApp DOM/DOM-Obs)│ <───────────────────── │ (Render Cloud Hosting) │
└────────────────────────┘  JSON Response Schema  └────────────────────────┘
            │                                                 │
            ▼                                                 ▼
   ┌─────────────────┐                               ┌─────────────────┐
   │ Memory Caching  │                               │ Detection Blend │
   │ & Local Storage │                               │ (langdetect +   │
   └─────────────────┘                               │  deep-translator)
                                                     └─────────────────┘
