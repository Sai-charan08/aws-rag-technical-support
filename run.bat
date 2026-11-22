@echo off
title AWS Technical Support RAG Assistant
echo ===================================================
echo   Starting AWS Technical Support Assistant Server
echo ===================================================
set PORT=8000
set PYTHONUNBUFFERED=1
python api/index.py
pause
