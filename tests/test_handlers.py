import os
import random
from datetime import datetime, timedelta, timezone
import dotenv
import pytest
from linebot.models.events import MessageEvent
from requests import delete

from FirebaseHandler import FirebaseHandler
from MessageEventHandler import MessageEventHandler


test_user_id = "Uf0000000000000000000000000000000"


class TestMessageEventHandler:
    def setup(self):

        dotenv.load_dotenv("../.env.yaml")

        self.firebase_handler = FirebaseHandler()
        self.message_event_handler = MessageEventHandler()
        self.mock_data = {
            "data": [
                "Boston Terrier",
                "Kokoni",
                "Toy Fox Terrier",
                "Pražský Krysařík",
                "Weimaraner",
                "Pastore della Lessinia e del Lagorai",
            ]
        }

        # put some data into dataset
        self.mock_database()

    def teardown(self):
        self.clean_dataset()

    def test_date(self):

        # run test function
        reply_messages = self.message_event_handler(self.mock_event("date"))

        except_result = datetime.utcnow().replace(tzinfo=timezone.utc)
        except_result.astimezone(timezone(timedelta(hours=8)))  # UTC+8
        except_result = [except_result.today().strftime("%Y-%m-%d")]

        assert reply_messages == except_result

    def test_list_data(self):
        reply_messages = self.message_event_handler(
            self.mock_event("list"),
        )

        # except result
        except_result = [
            "清單：\n"
            + "".join(
                [f"{i}. {d}\n" for i, d in enumerate(self.mock_data["data"])]
            ).strip()
        ]

        assert reply_messages == except_result

    def test_delete_data_by_text(self):

        delete_message = "Boston Terrier"

        # run test function
        reply_messages = self.message_event_handler(
            self.mock_event(f"delete {delete_message}"),
        )

        result_data = self.mock_data
        result_data["data"].remove(delete_message)

        data_after = self.read_data_raw()

        # test dataset
        assert data_after == result_data

        except_result = [
            f"已經刪除: {delete_message}",
            "清單：\n"
            + "".join(
                [f"{i}. {d}\n" for i, d in enumerate(result_data["data"])]
            ).strip(),
        ]

        # test reply message
        assert reply_messages == except_result

    def test_delete_data_by_index(self):
        delete_index = 0
        delete_message = self.mock_data["data"][delete_index]

        # run test function
        reply_messages = self.message_event_handler(
            self.mock_event(f"delete {delete_index}"),
        )

        result_data = self.mock_data
        result_data["data"].remove(delete_message)

        data_after = self.read_data_raw()

        # test dataset
        assert data_after == result_data

        # except result
        except_result = [
            f"已經刪除: {delete_message}",
            "清單：\n"
            + "".join(
                [f"{i}. {d}\n" for i, d in enumerate(result_data["data"])]
            ).strip(),
        ]

        # test reply message
        assert reply_messages == except_result

    def test_delete_data_not_in_database(self):

        delete_message = "Not in dataset data"

        # run testing fucntion
        reply_messages = self.message_event_handler(
            self.mock_event(f"delete {delete_message}"),
        )

        data_after = self.read_data_raw()
        result_data = self.mock_data

        # test dataset
        assert data_after == result_data

        except_result = [
            f"沒有 {delete_message} 的記錄",
            "清單：\n"
            + "".join(
                [f"{i}. {d}\n" for i, d in enumerate(self.mock_data["data"])]
            ).strip(),
        ]

        # test reply message
        assert reply_messages == except_result

    def test_remember_data(self):
        remember_message = "Staffordshire Bull Terrier"

        # run testing fucntion
        reply_messages = self.message_event_handler(
            self.mock_event(f"{remember_message}"),
        )

        result_data = self.mock_data
        result_data["data"].append(remember_message)
        data_after = self.read_data_raw()

        # test dataset
        assert data_after == result_data

        except_result = [
            f"已記住 {remember_message}",
            "清單：\n"
            + "".join(
                [f"{i}. {d}\n" for i, d in enumerate(self.mock_data["data"])]
            ).strip(),
        ]

        # test reply message
        assert reply_messages == except_result

    def read_data_raw(self):
        data: dict | None = self.firebase_handler.fb.get(
            self.firebase_handler.firebase_url + "users/" + test_user_id, None
        )
        return data

    def mock_event(self, message):
        return MessageEvent(
            mode="active",
            message={"id": "00000000000000", "text": message, "type": "text"},
            source={"type": "user", "userId": test_user_id},
            reply_token="da3f4677d5684e9f8fbe8637a5fdc790",
            timestamp="da3f4677d5684e9f8fbe8637a5fdc790",
        )

    def clean_dataset(self):

        self.firebase_handler.fb.put(
            self.firebase_handler.firebase_url + "users/", name=test_user_id, data=[]
        )

    def mock_database(self):

        self.firebase_handler.fb.put(
            self.firebase_handler.firebase_url + "users/",
            name=test_user_id,
            data=self.mock_data,
        )


class TestFirebaseHandler:
    def setup(self):

        dotenv.load_dotenv("../.env.yaml")
        CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")
        FIREBASE_URL = os.getenv("FIREBASE_URL", "")

        assert CHANNEL_ACCESS_TOKEN
        assert FIREBASE_URL

        self.firebase_handler = FirebaseHandler(FIREBASE_URL)
        self.mock_data = {
            "data": [
                "Boston Terrier",
                "Kokoni",
                "Toy Fox Terrier",
                "Pražský Krysařík",
                "Weimaraner",
                "Pastore della Lessinia e del Lagorai",
            ]
        }

        # put some data into dataset
        self.mock_database()

    def teardown(self):
        self.clean_dataset()

    def test_read(self):

        data = self.firebase_handler.read(test_user_id)

        except_result = self.mock_data

        assert data == except_result

    def test_write(self):
        write_data = "Exotic Shorthair"

        # test function
        self.firebase_handler.write(test_user_id, write_data)

        # Except result
        except_result = self.mock_data
        except_result["data"].append(write_data)

        # read data
        data: dict | None = self.read_data_raw()

        assert data == except_result

    def test_write_on_empty_database(self):
        self.clean_dataset()

        write_data = "Exotic Shorthair"

        # test function
        self.firebase_handler.write(test_user_id, write_data)

        # Except result
        except_result = {"data": [write_data]}

        # read data
        data: dict | None = self.read_data_raw()

        assert data == except_result

    def test_create(self):
        write_data = "Exotic Shorthair"

        # test function
        self.firebase_handler.create(test_user_id, write_data)

        # Except result
        except_result = {"data": [write_data]}

        # read data
        data: dict | None = self.read_data_raw()

        assert data == except_result

    def test_delete(self):

        delete_data = "Boston Terrier"

        # test function
        self.firebase_handler.delete(test_user_id, delete_data)

        # Except result
        except_result = self.mock_data
        except_result["data"].remove(delete_data)

        # read data
        data: dict | None = self.read_data_raw()

        assert data == except_result

    def read_data_raw(self):
        data: dict | None = self.firebase_handler.fb.get(
            self.firebase_handler.firebase_url + "users/" + test_user_id, None
        )
        return data

    def clean_dataset(self):

        self.firebase_handler.fb.put(
            self.firebase_handler.firebase_url + "users/", name=test_user_id, data=[]
        )

    def mock_database(self):

        self.firebase_handler.fb.put(
            self.firebase_handler.firebase_url + "users/",
            name=test_user_id,
            data=self.mock_data,
        )
