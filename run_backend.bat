@echo off
cd /d D:\ELE\backend
E:\ANACONDA\envs\ele-agent\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info