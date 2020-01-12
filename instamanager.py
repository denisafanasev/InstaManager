from instagram_private_api import Client, ClientCompatPatch, ClientError
from datetime import datetime
import time
import logging
import json
import ast

BLOCKED_USERS_CONTROL_LIST_FILENAME = "blockedlist.usr"
LOG_FILENAME = "socialguard.log"
LOGGING_LEVEL = logging.INFO
BLOCKING_LOG_FILENAME = "blocking.log"
MAX_TIMEOUT = 20


class InstaManager:
        
        _connections, _blocked_list = dict()

        _blocked_control_list = []
        _blocked_control_list_filename = BLOCKED_USERS_CONTROL_LIST_FILENAME

        _is_timeout = dict()

        def __init__(self):
                """Constructor"""

                logging.basicConfig(filename=LOG_FILENAME, level=LOGGING_LEVEL)
                logging.info("{}: session started".format(
                    str(datetime.now())))

                self.read_blocked_users_control_list()  # Initially reaading a infinity blocked users list

                pass

        def _timeout_call(self, account_name):
                """
                Internal function to allign with IS request timing policy
                @params:
                        account_name   - Required  : account name for api call
                """
                time_diff = datetime.timestamp(
                    datetime.now()) - self._is_timeout.get(account_name)

                time.sleep(MAX_TIMEOUT - max(0, 10 - time_diff))

                self._is_timeout[account_name] = datetime.timestamp(
                    datetime.now())

                pass

        def read_blocked_users_list(self, account_name):
                """
                Function read blocked users list from the account by account_name
                @params:
                        param1   - Required  : description
                """

                logging.info("{}:{}: getting blocked users list".format(str(datetime.now()), str(account_name)))
                _items = []
                try:
                        _api = self._connections.get(account_name)

                        rank_token = _api.generate_uuid()
                        _result = _api.blocked_user_list(rank_token)
                        _items.extend(_result.get('blocked_list', []))

                        next_max_id = _result.get('next_max_id')
                        while next_max_id:
                                self._timeout_call(account_name)
                                _result = _api.blocked_user_list(rank_token, max_id=next_max_id)
                                _items.extend(_result.get('blocked_list', []))
                                next_max_id = _result.get('next_max_id')

                        self._blocked_list[account_name] = _items

                        logging.info("{}:{}: getting blocked users list successed".format(
                            str(datetime.now()), str(account_name)))
                except ClientError as e:
                        logging.error("{}:{}: getting blocked users list failed: {}".format(str(datetime.now()), str(account_name), str(account_name), e.msg))
                pass

        def read_blocked_users_control_list(self):
                """
                Function read blocked users from saved file
                @params:
                        param1   - Required  : description
                """

                logging.info("{}: reading blocked control file".format(str(datetime.now())))
                self._blocked_control_list.clear()

                try:
                        file_iter = open(
                            "data/" + BLOCKED_USERS_CONTROL_LIST_FILENAME, 'rU')
                        for line in file_iter:
                                self._blocked_control_list.append(ast.literal_eval(line))

                        logging.info("{}: reading blocked control file successed".format(str(datetime.now())))

                except Exception:
                        logging.error("{}: reading blocked control file: failed".format(
                            str(datetime.now())))
                pass

        def save_user_list(self, users, filename):
                """
                write a user list to file with filename
                @params:
                        param1   - Required  : description
                """

                try:
                        with open("data/" + filename, 'w') as f:
                                for item in users:
                                        f.write(str(item) + "\n")
                        f.close()
                        logging.info(
                            "{}:{} - wrote successful".format(str(datetime.now()), filename))
                except Exception:
                        logging.error(
                            "{}:{} -  wrote failed".format(str(datetime.now()), filename))
                pass

        def save_blocked_users_control_list(self):
                """
                Function write blocked users from saved file
                @params:
                        param1   - Required  : description
                """

                logging.info("{}: writing blocked control file".format(str(datetime.now())))
                self.save_user_list(self._blocked_control_list, BLOCKED_USERS_CONTROL_LIST_FILENAME)

                pass

        def get_blocked_users_control_list(self):
                """
                Function get blocked users control list
                @params:
                        param1   - Required  : description
                """

                return self._blocked_control_list

        def merge_user_lists(self, user_list1, user_list2):
                """
                merge two lists together
                @params:
                        param1   - Required  : description
                """

                _list = user_list1
                for element2 in user_list2:
                        _check = False
                        for element1 in user_list1:
                                if element1['user_id'] == element2["user_id"]:
                                        _check = True
                                        break

                        if not _check:
                                _list.append(element2)

                return _list

        def diff_user_lists(self, user_list1, user_list2):
                """
                return a users from list 2 which is no in list1
                @params:
                        param1   - Required  : description
                """

                _list = []
                for element2 in user_list2:
                        _check = False
                        for element1 in user_list1:
                                if element1['user_id'] == element2["user_id"]:
                                        _check = True
                                        break

                        if not _check:
                                _list.append(element2)

                return _list

        def add_users_to_blocked_users_control_list(self, user_list):
                """
                Adding users to blocked user control list
                @params:
                        param1   - Required  : description
                """

                _to_add = self.diff_user_lists(self._blocked_control_list, user_list)
                self._blocked_control_list.extend(_to_add)

                pass

        def get_blocked_users_list(self, account_name):
                """Return blocked users list for the account
                @params:
                        param1   - Required  : description
                """

                return self._blocked_list.get(account_name)

        def connect(self, account_name, password):
                """ Connect to an account in IS
                Trying to connect to the account        
                and add a new connection to the conecction pool
                @params:
                        account_name   - Required  : description
                        password       - Required  : description
                """

                try:
                        logging.info("{}:{}: connecting".format(
                            str(datetime.now()), str(account_name)))
                        self._is_timeout[account_name] = datetime.timestamp(
                            datetime.now())
                        api = Client(account_name, password)
                        self._connections[account_name] = api
                        logging.info("{}:{}: connected".format(
                            str(datetime.now()), str(account_name)))

                        # For each new connection initialy read blocked user list
                        self.read_blocked_users_list(account_name)

                        return True
                except ClientError as e:
                        logging.error(
                            "{}:{}: connected failed: {}".format(str(datetime.now()), account_name, e.msg))
                        return False

        def get_connections(self):
                """
                Get connections list as a dict
                """
                result = []
                for key in self._connections.keys():
                        result.append(key)
                return result

        def get_blocked_status(self, account_name, user):
                """
                Check if user is blocked
                @params:
                        account_name   - Required  : account name
                        user           - Required  : user for status check
                """

                try:
                        _api = self._connections.get(account_name)
                        result = _api.friendships_show(user['user_id'])
                        return result['blocking']
                except ClientError as e:
                        logging.error("{}:{}: user {} id {} status check error: {}".format(str(datetime.now()), str(account_name), user['username'], user['user_id'], e.msg))
                        return True

        def block_user(self, account_name, user):
                """
                Block user
                @params:
                        account_name   - Required  : account name
                        user           - Required  : user for block
                """

                _api = self._connections.get(account_name)
                self._timeout_call(account_name)
                try:
                        result = _api.friendships_block(user['user_id'])
                        if result['status'] == 'ok':
                                logging.info("{}:{}: user {}: blocked".format(str(datetime.now()), str(account_name), str(user['user_id'])))
                                try:
                                        with open("data/" + BLOCKING_LOG_FILENAME, 'a') as f:
                                                f.write(str(datetime.now()) +
                                                        ":" + account_name + ":" + str(user) + "\n")
                                        f.close()
                                except Exception:
                                        pass
                        else:
                                logging.info("{}:{}: user {}: block failed".format(
                                    str(datetime.now()), str(account_name), str(user['user_id'])))
                                pass
                        pass
                except ClientError as e:
                        logging.error("{}:{}: user {} id {} blocking error: {}".format(str(datetime.now()), str(account_name), user['username'], user['user_id'], e.msg))

                        return False

                return True
