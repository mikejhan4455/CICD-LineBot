from datetime import datetime, timedelta, timezone
import re
from typing import Any
from FirebaseHandlerAdmin import FirebaseHandler


class MessageEventHandler:
    def __init__(self) -> None:
        self.firebase_handler = FirebaseHandler()

    def __call__(self, event):

        message: str = event.message.text
        user_id: str = event.source.user_id

        user_data = self.get_user_data(user_id)

        # message route
        if re.match("list", message, re.IGNORECASE):

            return self.list_data(user_id)

        # Delete format: with keyword or without keyword
        if (
            re.match("delete", message, re.IGNORECASE)
            or bool(message in user_data)
            or message.isdigit()
        ):

            return self.delete_data(user_id, message, user_data)

        if re.match("search", message, re.IGNORECASE):

            return self.search_data(user_id, message)

        # access function table test
        if re.match("fuction", message, re.IGNORECASE):
            return self.add_functions(user_id, message)

        # 其他一律存入 database
        return self.remember_data(user_id, message, user_data)

    def date(self):
        reply_message = []
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt.astimezone(timezone(timedelta(hours=8)))  # UTC+8

        reply_message.append(dt.today().strftime("%Y-%m-%d"))

        return reply_message

    def list_data(self, user_id: str):
        reply_message = []

        # update user_data
        user_data = self.get_user_data(user_id)

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
            3. without keyword: If message already in user_data

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
        remove_data = message.split()

        for idx, data in enumerate(remove_data):
            # if index is given, transform to text
            if data.isdigit():
                data = int(data)

                # change index to text
                remove_data[idx] = user_data[data] if data < len(user_data) else data

            # if data is in user_data, add a message
            if data in user_data:
                reply_message.append(f"已刪除 {data}")

            else:
                reply_message.append(f"沒有 {message} 的記錄")

        # remove by text
        self.firebase_handler.remove_user_data(user_id, remove_data)

        reply_message.extend(self.list_data(user_id))

        return reply_message

    def remember_data(self, user_id, message, user_data):
        reply_message = []
        data = message.split()
        self.firebase_handler.add_user_data(user_id, data)

        # reply success
        for d in data:
            reply_message.append(f"已記住 {message}")

        # reply current database
        reply_message.extend(self.list_data(user_id))

        return reply_message

    def search_data(self, user_id: str, message: str):
        # TODO: under Testing
        reply_message = []

        # search my index or re
        user_data = self.get_user_data(user_id)

        # remove keyword "search"
        insensitive_search = re.compile(re.escape("search"), re.IGNORECASE)
        message = insensitive_search.sub("", message).strip()
        message = message.split()

        if not user_data:
            reply_message.append("目前沒有資料噢")

        # search by index
        elif message[0].isdigit():
            index = int(message[0])
            if index < len(user_data):
                reply_message.append(user_data[index])

            else:
                reply_message.append("沒有這個索引")

        # search inline
        else:
            search_data = " ".join(message)
            search_data = search_data.replace(" ", ".*")
            search_data = f".*{search_data}.*"

            for data in user_data:
                if re.match(search_data, data, re.IGNORECASE):
                    reply_message.append(data)

        return reply_message

    def add_functions(self, user_id: str, message: str):
        reply_message = []

        # remove keyword
        insensitive_function = re.compile(re.escape("function"), re.IGNORECASE)
        message = insensitive_function.sub("", message).strip()
        data = message.split()

        print(data)

        funcs = data[0] if 0 < len(data) else "MyDefaultFunc()"
        hours = data[1] if 1 < len(data) else None
        minutes = data[2] if 2 < len(data) else None

        self.firebase_handler.add_user_funcs_map(
            user_id, funcs=funcs, hours=hours, minutes=minutes
        )

        # reply success
        reply_message.append(f"已記住 {message}")

        # reply current database
        reply_message.extend(self.list_data(user_id))

        return reply_message

    def get_user_data(self, user_id) -> list:
        user_data: dict | None = self.firebase_handler.read_user_data(user_id)  # type: ignore
        user_data: list = user_data if user_data else []  # type: ignore

        return user_data
