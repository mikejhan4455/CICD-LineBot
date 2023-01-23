from itertools import product
import os
from typing import List, Optional

import dotenv
import firebase_admin
from firebase_admin import credentials, db
import numpy as np


class FirebaseHandler:
    def __init__(self, firebase_url=None) -> None:

        if firebase_url:
            self.firebase_url = firebase_url
        else:
            # get firebase_url from environment variables
            dotenv.load_dotenv(".env.yaml")
            self.firebase_url = os.getenv("FIREBASE_URL") or ""

        # Exception handler
        if not self.firebase_url:
            raise Exception(
                "Please specify firebase_url from parameter or with environment variable"
            )

        # Auth Step
        self.fire_base_cert = {
            "type": os.getenv("FIRE_BASE_CERT_TYPE"),
            "project_id": os.getenv("FIRE_BASE_CERT_PROJECT_ID"),
            "private_key_id": os.getenv("FIRE_BASE_CERT_PRIVATE_KEY_ID"),
            "private_key": bytes(
                os.getenv("FIRE_BASE_CERT_PRIVATE_KEY"), "utf-8"
            ).decode("unicode_escape"),
            "client_email": os.getenv("FIRE_BASE_CERT_CLIENT_EMAIL"),
            "client_id": os.getenv("FIRE_BASE_CERT_CLIENT_ID"),
            "auth_uri": os.getenv("FIRE_BASE_CERT_AUTH_URI"),
            "token_uri": os.getenv("FIRE_BASE_CERT_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv(
                "FIRE_BASE_CERT_AUTH_PROVIDER_X509_CERT_URL"
            ),
            "client_x509_cert_url": os.getenv("FIRE_BASE_CERT_CLIENT_X509_CERT_URL"),
        }

        # Fetch the service account key JSON file contents
        cret = credentials.Certificate(self.fire_base_cert)
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cret, {"databaseURL": self.firebase_url})

    def __read(self, user_id, node):
        ref = db.reference(f"/users/{user_id}/{node}")
        data = ref.get()
        return data

    def __write(self, user_id, node, data):
        ref = db.reference(f"/users/{user_id}/{node}")
        ref.set(data)

    def __delete(self, user_id, node):
        ref = db.reference(f"/users/{user_id}/{node}")
        ref.delete()

    def __remove_Nones(self, data):

        # 3d array
        if isinstance(data[0][0], list):
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = [d for d in data[i][j] if d != "None"]
            return data

        # 1d array
        return [d for d in data if d != "None"]

    def __add_Nones(self, data):
        # 3d array
        if isinstance(data[0][0], list):
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = ["None"] + data[i][j]
            return data
        # 1d array
        return ["None"] + data

    def read_user_data(self, user_id):

        user_data = self.__read(user_id, "data")

        if user_data is None:
            self.create_user_data_list(user_id)

        user_data = self.__read(user_id, "data")

        return self.__remove_Nones(user_data)

    def create_user_data_list(self, user_id):
        user_data = ["None"]

        self.__write(user_id, "data", user_data)

    def add_user_data(self, user_id, data):
        user_data: list = self.read_user_data(user_id)
        user_data.extend(data)

        user_data = list(dict.fromkeys(user_data))  # remove duplicate
        user_data = self.__add_Nones(user_data)  # Recover "None" to indicate no data

        self.__write(user_id, "data", user_data)

    def remove_user_data(self, user_id, data: list):
        user_data: list = self.read_user_data(user_id)

        if len(data) == 0:
            self.create_user_data_list(user_id)
            return

        for d in data:
            if d in user_data:
                user_data.remove(d)

        user_data = self.__add_Nones(user_data)  # Recover "None" to indicate no data

        self.__write(user_id, "data", user_data)

    def clear_user_data(self, user_id):
        self.__write(user_id, "data", ["None"])

    def read_user_funcs_map(self, user_id):

        funcs_map = self.__read(user_id, "func")

        # check funcs_map initialized
        if funcs_map is None:
            self.create_user_funcs_map(user_id)

        funcs_map = self.__read(user_id, "func")

        # remove "None" from list
        funcs_map = self.__remove_Nones(funcs_map)

        return funcs_map

    def create_user_funcs_map(self, user_id):
        funcs_map = np.zeros((24, 4), object)

        for i in range(funcs_map.shape[0]):
            for j in range(funcs_map.shape[1]):
                funcs_map[i][j] = [
                    "None"
                ]  # First item will remain "None" to indicate no task, prevent from empty list

        print(funcs_map)

        self.__write(user_id, "func", funcs_map.tolist())

    def add_user_funcs_map(
        self,
        user_id,
        funcs: list,
        hours=None,
        minutes=None,
    ):

        if not hours:
            hours = [i for i in range(24)]
        if not minutes:
            minutes = [i for i in range(4)]

        # turn hours minutes funcs to list if not
        if isinstance(hours, str):
            hours = [int(hours)]
        if isinstance(minutes, str):
            minutes = [int(minutes)]
        if not isinstance(funcs, list):
            funcs = [funcs]

        funcs_map = self.read_user_funcs_map(user_id)

        for h, m in product(hours, minutes):
            funcs_map[h][m].extend(funcs)
            funcs_map[h][m] = list(dict.fromkeys(funcs_map[h][m]))  # remove duplicate

        # add "None" to list
        funcs_map = self.__add_Nones(funcs_map)

        self.__write(user_id, "func", funcs_map)

    def remove_user_funcs_map(
        self,
        user_id,
        funcs: list,
        hours: Optional[list] = None,
        minutes: Optional[list] = None,
    ):
        """
        Remove functions from user's funcs map

        Args:
            user_id (_type_): line user_id
            funcs (list): list of functions that want to remove, e.g. ['func1', 'func2'], if empty, remove all functions
            hours (Optional[list], optional): _description_. Defaults to None.
            minutes (Optional[list], optional): from 0 to 3, represent 0, 15, 30, 45 . Defaults to None, represent all four.
        """
        if not hours:
            hours = [i for i in range(24)]
        if not minutes:
            minutes = [i for i in range(4)]

        # turn hours minutes to list if not
        if not isinstance(hours, list):
            hours = [hours]
        if not isinstance(minutes, list):
            minutes = [minutes]

        funcs_map = self.read_user_funcs_map(user_id)

        if len(funcs) == 0:
            self.create_user_funcs_map(user_id)
            return

        # remove specific functions
        for h, m, f in product(hours, minutes, funcs):
            if f in funcs_map[h][m]:
                funcs_map[h][m].remove(f)

        # add "None" to list
        funcs_map = self.__add_Nones(funcs_map)

        self.__write(user_id, "func", funcs_map)


def test():
    fh = FirebaseHandler()
    user_id = "00000"

    # fh.create_user_funcs_map(user_id)

    # data
    # fh.add_user_data(user_id, ['1', '2', '3', '4'])
    # print(fh.read_user_data(user_id))

    # # function
    # fh.add_user_funcs_map(user_id, ['1', '2', '3', '4'])
    # print(fh.read_user_funcs_map(user_id))

    # fh.remove_user_funcs_map(user_id, [])
    # print(fh.read_user_funcs_map(user_id))

    fh.remove_user_data(user_id, [])


def test_cert():
    pass


if __name__ == "__main__":

    test()
