import os
import requests
import json
import dotenv


dotenv.load_dotenv(".env.yaml")

headers = {
    "Authorization": "Bearer {}".format(os.getenv("CHANNEL_ACCESS_TOKEN")),
    "Content-Type": "application/json",
}
body = {
    "to": os.getenv("PERSONAL_USERID"),
    "messages": [
        {
            "type": "text",
            "text": "Github Action Finished, test result ->  {}".format(
                os.getenv("TEST_STATUS")
            ),
        }
    ],
}
# 向指定網址發送 request
req = requests.request(
    "POST",
    "https://api.line.me/v2/bot/message/push",
    headers=headers,
    data=json.dumps(body).encode("utf-8"),
)
# 印出得到的結果
print(req.text)
