import os
from firebase import firebase


class FirebaseHandler:
    def __init__(self, firebase_url=None) -> None:
        # TODO: Add Auth step

        if firebase_url:
            self.firebase_url = firebase_url
        else:
            # get firebase_url from environment variables
            self.firebase_url = os.getenv("FIREBASE_URL") or ""

        # Exception handler
        if not self.firebase_url:
            raise Exception(
                "Please specify firebase_url from parameter or with environment variable"
            )

        self.fb = firebase.FirebaseApplication(self.firebase_url, None)

    def read(self, user_id):

        data: dict = self.fb.get(self.firebase_url + "users/" + user_id, None)
        return data

    def write(self, user_id, data):

        user_data = self.read(user_id)

        if not user_data:
            # No record created yet, create one
            self.create(user_id, data)

        else:
            # User record exist, append data
            user_data["data"].append(data)
            self.fb.put(self.firebase_url + "users/", name=user_id, data=user_data)

    def create(self, user_id, data):

        # Creating a record must provide some data
        data = {"data": [data]}
        self.fb.put(self.firebase_url + "users/", name=user_id, data=data)

    def delete(self, user_id, data):
        user_data = self.read(user_id)

        if not user_data:
            # data not exist
            return None

        elif data in user_data["data"]:
            user_data["data"].remove(data)
            self.fb.put(self.firebase_url, name="users", data=user_data)
            return True
