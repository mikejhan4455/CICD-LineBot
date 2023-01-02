from datetime import datetime, timedelta, timezone
from FirebaseHandler import FirebaseHandler


class MessageEventHandler:
    def __init__(self) -> None:
        self.firebase_handler = FirebaseHandler()

    def __call__(self, event):

        message = event.message.text
        user_id = event.source.user_id

        # message route
        if message == "date":
            self.date()

        if message.startswith("list"):
            self.list_data(user_id)

        if message.startswith("delete"):
            self.delete_data(user_id, message)

        if message.startswith("remind"):
            self.remind_data(user_id, message)

    def date(self):
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

        reply_text = dt.today().strftime("%Y-%m-%d")

        return reply_text

    def list_data(self, user_id):
        data = self.firebase_handler.read(user_id)

        reply_text = "".join(
            ["{}. {}\n".format(i, d) for i, d in enumerate(data["data"])]
        )

        return reply_text

    def delete_data(self, user_id, message):

        result = self.firebase_handler.delete(user_id, message)

        if result:
            reply_text = "已經刪除: {}".format(message)
        else:
            reply_text = "沒有 {} 的記錄".format(message)

        return reply_text

    def remind_data(self, user_id, message):
        # TODO：WIP

        reply_text = ""

        return reply_text
