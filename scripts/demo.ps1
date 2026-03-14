
# scripts/demo.ps1
# 运行前确保服务已启动

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

curl.exe -X POST "http://127.0.0.1:8010/analyze" `
  -H "accept: application/json" `
  -F "image=@E:\python\test6\images\sample.jpg;type=image/jpeg" `
  -F "goal=请描述图片内容，并总结关键物体与细节，输出要点报告" `
  -F "session_id=default" `
  -F "offline=true" `
  -F "max_new_tokens=40"
