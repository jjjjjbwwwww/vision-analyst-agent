$ErrorActionPreference = "Stop"

# 1) test6
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd E:\python\test6; conda activate torch; python -m uvicorn app:app --host 127.0.0.1 --port 8006"
)

# 2) test7
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd E:\python\test7; conda activate torch; uvicorn api:app --host 127.0.0.1 --port 8007"
)

# 3) project3 analyst_api
Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd E:\python\project2\vision_analyst_agent; conda activate torch; uvicorn app.analyst_api:app --host 127.0.0.1 --port 8010"
)

Write-Host "✅ started: test6(8006), test7(8007), analyst(8010)"
Write-Host "Open UI: http://127.0.0.1:8010/ui.html"