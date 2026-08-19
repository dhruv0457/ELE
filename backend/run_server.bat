@echo off
cd /d D:\ELE\backend
E:\ANACONDA\condabin\conda.bat run -n ele-agent python -m uvicorn app.main:app --host 127.0.0.1 --port 8000