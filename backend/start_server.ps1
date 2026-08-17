Set-Location "D:\ELE\backend"
& "E:\ANACONDA\envs\ele-agent\python.exe" -m uvicorn app.main:app --host localhost --port 8000 *> "D:\ELE\backend\server.log"
