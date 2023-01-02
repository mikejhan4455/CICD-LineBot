from datetime import datetime, timedelta, timezone
import re
from FirebaseHandler import FirebaseHandler


class MessageEventHandler:
    def __init__(self) -> None:
        self.firebase_handler = FirebaseHandler()

    def __call__(self, event):

        message = event.message.text
        user_id = event.source.user_id

        # message route
        if message == "date":
            return self.date()

        if re.match("list", message, re.IGNORECASE):

            return self.list_data(user_id)

        if re.match("delete", message, re.IGNORECASE):

            return self.delete_data(user_id, message)

        if re.match("remind", message, re.IGNORECASE):

            return self.remind_data(user_id, message)

        # 其他一律存入 database
        return self.remember_data(user_id, message)

    def date(self):
        reply_message = []
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

        reply_message.append(dt.today().strftime("%Y-%m-%d"))

        return reply_message

    def list_data(self, user_id: str):
        reply_message = []
        data = self.firebase_handler.read(user_id)

        if not data:
            reply_message.append("目前沒有資料噢")

        else:
            reply_message.append(
                "清單：\n" + "".join(
                    ["{}. {}\n".format(i, d) for i, d in enumerate(data["data"])]
                ).strip()
            )

        return reply_message

    def delete_data(self, user_id: str, message: str):

        reply_message = []

        # remove keyword
        insensitive_delete = re.compile(re.escape("delete"), re.IGNORECASE)
        message = insensitive_delete.sub("", message).strip()

        # remove by index or text
        if message.isdigit():
            # remove by index
            index = int(message)
            # BUG: Delete index out of range
            message = self.firebase_handler.read(user_id)["data"][index]
            result = self.firebase_handler.delete(user_id, message)

        else:
            # remove by text
            result = self.firebase_handler.delete(user_id, message)

        if result:
            reply_message.append("已經刪除: {}".format(message))
        else:
            reply_message.append("沒有 {} 的記錄".format(message))

        reply_message.extend(self.list_data(user_id))

        return reply_message

    def remember_data(self, user_id, message):
        reply_message = []
        self.firebase_handler.write(user_id, message)

        # reply success
        reply_message.append("已記住 {}".format(message))

        # reply current database
        reply_message.extend(self.list_data(user_id))

        return reply_message

    def remind_data(self, user_id: str, message: str):
        # TODO：WIP

        reply_message = []

        return reply_message

    def search_dat(self, user_id: str, message: str):
        # TODO: WIP
        reply_message = []

        return reply_message
