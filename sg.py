import ada as ada
from datetime import datetime
import time
from random import randint
from instamanager import InstaManager as SocialGuard
import toml
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='It is a console interface for InstaManager')

    parser.add_argument('-c', dest='config_file', default="black_list_merge.toml",
                    help='Config file')

    args = parser.parse_args()

    print("{}-------------------------{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))
    print("{}Social guard 0.3 starting{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))
    print("{}-------------------------{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))
    print("")

    print("config file: {}".format(args.config_file))
    config = toml.load(args.config_file.strip())

    _sg = SocialGuard()

    for connection in config["connection"]:
        if connection["active"]:
            print("{} connecting:".format(connection["name"]), end='\r')
            if connection["active"] is True:

                user_name = connection["name"]
                password = connection["password"]

                result = _sg.connect(user_name, password)

                if result:
                    print("{} connecting: {}OK{}".format(connection["name"],
                        ada.bcolors.OKGREEN, ada.bcolors.ENDC))
                else:
                    print("{} connecting: {}Failed{}".format(connection["name"],
                        ada.bcolors.FAIL, ada.bcolors.ENDC))

    print("blocked user control list: {}".format(str(len(_sg.get_blocked_users_control_list()))))
    print("")

    print("{}### - conection to Instagram:{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))


    print("")
    print("{}### - blocked users lists check:{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))
    blocked_user = _sg.diff_user_lists(_sg.get_blocked_users_control_list(), _sg.get_blocked_users_list(control_user_name))
    print("number of new blocked users: " + str(len(blocked_user)))

    unblocked_user = _sg.diff_user_lists(_sg.get_blocked_users_list(
        control_user_name), _sg.get_blocked_users_control_list())
    print("number of unblocked users: " + str(len(unblocked_user)))

    print("writing user lists diff to the files")
    _sg.save_user_list(unblocked_user, "unblocked_" + str(datetime.timestamp(datetime.now())) + ".usr")
    _sg.save_user_list(blocked_user, "blocked_" + str(datetime.timestamp(datetime.now())) + ".usr")

    print("")
    print("{}### - blocked users lists syncing:{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))

    # собираем все блок листы в единый список заблокированных пользователей
    for connection_name in _sg.get_connections():
        print(connection_name + ' block list len: ' + str(len(_sg.get_blocked_users_list(connection_name))))

        _sg.add_users_to_blocked_users_control_list(
            _sg.get_blocked_users_list(connection_name))

    print("merged blocked user control list: " + str(len(_sg.get_blocked_users_control_list())))

    # пишем в файл единый список блокировок
    print("blocked users control list file updating")
    _sg.save_blocked_users_control_list()

    to_block = _sg.diff_user_lists(
        _sg.get_blocked_users_list(control_user_name), _sg.get_blocked_users_control_list())
    print("number of users to block: " + str(len(to_block)))

    i = 0
    new_user_blocked = 0
    for user in to_block:
            i += 1
            ada.printProgressBar(i, len(
                to_block), prefix='Progress:', suffix='Complete', decimals=2, length=50)
            result = _sg.get_blocked_status(control_user_name, user)

            if result is False:
                    if _sg.block_user(control_user_name, user):
                        new_user_blocked += 1

    print("block list updating done, new users blocked: " + str(new_user_blocked))

    print("")
    print("{}All done{}".format(ada.bcolors.HEADER, ada.bcolors.ENDC))
