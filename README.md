순서
slack_webhook_url = "https://hooks.slack.com/services/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"
1. ngrok 실행
   -> slack은 local에서 flask로 올린 서버에 접근 불가능해서 우회
2. https://b37b-122-36-135-6.ngrok-free.app 와 같이 서버가 나오면
   -> slack api 접속 후 Your Apps-slash Commands에 입력해주기
   -> OAuth & Permissions 들어가서 Bot User OAuth Token 복사해서
   -> export SLACK_BOT_TOKEN="xoxb-XXXXXXXXXXXX-XXXXXXXXXXXX-XXXXXXXXXXXXXXXX"//안에 xoxb-~만 바꿔주면됨
   -> 이 명령어 cmd창에 입력

3. python app.py
4. python fetch_cookies.py -> 쿠키값 config.json에 들어오면 그 다음순서로
5. python ransom_monitor1.py
6. python ransom_monitor2.py
7. 
