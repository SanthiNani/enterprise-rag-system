---
title: Enterprise RAG Backend
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# Enterprise RAG System Backend

This is the backend for the Enterprise RAG System, deployed as a Docker container.

## Configuration

This Space expects the following secrets:
- `GEMINI_API_KEY`: Google Gemini API Key.
- `DATABASE_URL`: PostgreSQL Connection URL (e.g. from Neon).
- `SECRET_KEY`: Backend secret key.
