from abc import ABC
import datetime
import pytz
import utils
import storage

SGT_TIMEZONE = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    curr_user = None

    def __init__(self, name: str):
        self.name = name

    def get_name(self):
        return self.name

    def status(self):
        curr_user, end_time = storage.get_laundry_timer(self.name)
        if utils.is_available(end_time):
            reply = f"AVAILABLE \U00002705"
            if curr_user:
                reply += f', last used by @{curr_user} ({end_time.astimezone(SGT_TIMEZONE).strftime("%d/%m/%Y %I:%M%p")})'
            return reply
        else:
            time_delta = end_time - datetime.datetime.now()
            time_in_min = time_delta.seconds // 60
            time_in_sec = time_delta.seconds % 60
            return f"UNAVAILABLE \U0000274C for {time_in_min}mins and {time_in_sec}s by @{curr_user}"

    def get_curr_user(self):
        curr_user, end_time = storage.get_laundry_timer(self.name)
        return curr_user

    def start_machine(self, new_user: str, chat_id: int):
        _, end_time = storage.get_laundry_timer(self.name)
        if not utils.is_available(end_time):
            return False
        else:
            new_end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=Machine.COMPLETION_TIME
            )
            new_curr_user = new_user
            storage.set_laundry_timer(self.name, new_curr_user, new_end_time, chat_id)
            return True


Machine.COMPLETION_TIME = 1 * 60
