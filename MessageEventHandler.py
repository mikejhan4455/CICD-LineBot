from datetime import datetime, timedelta, timezone
import re
from typing import Any
from FirebaseHandler import FirebaseHandler


class MessageEventHandler:
    def __init__(self) -> None:
        self.firebase_handler = FirebaseHandler()

    def __call__(self, event):

        message = event.message.text
        user_id = event.source.user_id

        # get user_data
        user_data: dict | None = self.firebase_handler.read(user_id)  # type: ignore
        user_data: list = user_data["data"] if user_data else []  # type: ignore

        # message route
        if message == "date":
            return self.date()

        if re.match("list", message, re.IGNORECASE):

            return self.list_data(user_id, user_data)

        if re.match("delete", message, re.IGNORECASE) or bool(message in user_data):

            return self.delete_data(user_id, message, user_data)

        if re.match("remind", message, re.IGNORECASE):

            return self.remind_data(user_id, message)

        # 其他一律存入 database
        return self.remember_data(user_id, message, user_data)

    def date(self):
        reply_message = []
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

        reply_message.append(dt.today().strftime("%Y-%m-%d"))

        return reply_message

    def list_data(self, user_id: str, user_data: list):
        reply_message = []

        if not user_data:
            reply_message.append("目前沒有資料噢")

        else:
            reply_message.append(
                "清單：\n"
                + "".join([f"{i}. {d}\n" for i, d in enumerate(user_data)]).strip()
            )

        return reply_message

    def delete_data(self, user_id: str, message: str, user_data: list):
        """Delete data from user datbase
        now support format:  and keyword+index
        Example:
            1. keyword+word: delete 資料
            2. keyword+index: delete 3

        # TODO: Delete data without keyword

        Args:
            user_id (str): event.source.user_id
            message (str): event.message.text

        Returns:
            reply_message (list): reply messages
        """

        reply_message = []

        # remove keyword
        insensitive_delete = re.compile(re.escape("delete"), re.IGNORECASE)
        message = insensitive_delete.sub("", message).strip()

        # if index is given, transform to text data
        if message.isdigit():
            index = int(message)

            # change index to text
            message = user_data[index] if index < len(user_data) else message

        # remove by text
        result = self.firebase_handler.delete(user_id, message)

        if result:
            reply_message.append(f"已經刪除: {message}")
        else:
            reply_message.append(f"沒有 {message} 的記錄")

        reply_message.extend(self.list_data(user_id, user_data))

        return reply_message

    def remember_data(self, user_id, message, user_data):
        reply_message = []
        self.firebase_handler.write(user_id, message)

        # reply success
        reply_message.append("已記住 {message}")

        # reply current database
        reply_message.extend(self.list_data(user_id, user_data))

        return reply_message

    def remind_data(self, user_id: str, message: str):
        # TODO：WIP

        reply_message = []

        return reply_message

    def search_data(self, user_id: str, message: str):
        # TODO: WIP
        reply_message = []

        return reply_message
