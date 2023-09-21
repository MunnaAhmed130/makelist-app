import os
import re
import sys
import csv
import time
from tabulate import tabulate
from colorama import Fore, init

init(autoreset=True)

WELCOME = [
    ["Welcome to makelist app"],
    ["1. Sign up or register using email"],
    ["2. Login using email and password"],
    ["3. Exit"],
]

MENU = [
    ["Main menu"],
    ["1. Make a list"],
    ["2. View a list"],
    ["3. Edit a list"],
    ["4. Delete a list"],
    ["5. Exit"],
]


NAME_REGEX = r"^\w{3,}$"
EMAIL_REGEX = r"^^\w+\.?\w+@\w+(\.\w{2,3}){1,3}$"
PASSWORD_REGEX = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{4,}$"

NAME_ERR_MSG = "Enter more than 3 character"
EMAIL_ERR_MSG = "Invalid email address"
PASSWORD_ERR_MSG = "minimum 4 characters, 1 uppercase, 1 lowercase and 1 digit"


def main():
    while True:
        # welcome_page
        print_tabulate(WELCOME)

        first_option = choose_option(1, 3)
        log_in = match_welcome_option(first_option)

        if log_in:
            print_message(Fore.GREEN + "Successfully " + log_in)
        else:
            continue

        while True:
            # main menu
            print_tabulate(MENU)

            menu_option = choose_option(1, 5)
            match_menu_option(menu_option)

            sleep()


# make page


def page(csv_file):
    lines = csv_reader(csv_file)
    print_tabulate(lines)


def print_tabulate(data):
    print(
        tabulate(
            data,
            headers="firstrow",
            tablefmt="mixed_outline",
            stralign="center",
            numalign="center",
        )
    )

    sleep()


# user options


def choose_option(min, max):
    while True:
        try:
            sleep()
            option = int(input("choose your option: "))
            if validate_option(option, min, max):
                return option
            else:
                print(Fore.RED + "choose from the options given above")

        except ValueError:
            print(Fore.RED + "input has to be a number")


def validate_option(value, min, max):
    if (value > max) | (value < min):
        return False
    else:
        return True


def match_welcome_option(option):
    match option:
        case 1:
            return sign_up()
        case 2:
            return sign_in()
        case _:
            terminate_program()


def match_menu_option(option):
    match option:
        case 1:
            make_list()
        case 2:
            view_list()
        case 3:
            edit_list()
        case 4:
            delete_list()
        case _:
            terminate_program()


def terminate_program():
    print_message(Fore.RED + "programme terminated")
    sys.exit()


# authentication options


def user_already_exist(email_address):
    user_list = csv_reader("users.csv", dict=True)
    for user in user_list:
        if user["email_address"] == email_address:
            return True
        else:
            return False


def sign_up():
    print_message("To skip press enter")
    sleep()

    csv_file = "users.csv"
    check_csv(csv_file)
    # user_list = csv_reader(csv_file, dict=True)

    username = user_name()
    email_address = user_email_address()
    password = user_password()

    if user_already_exist(email_address):
        print_message(Fore.RED + "user already exists")
        return

    user = {"username": username, "email_address": email_address, "password": password}

    # print(user)
    if (username == "") or (email_address == "") or (password == ""):
        print_message("Back to welcome page")
        return

    with open(csv_file, "a", newline="\n") as users:
        writer = csv.DictWriter(
            users, fieldnames=["username", "email_address", "password"]
        )
        writer.writerow(user)

    return "registered"


def sign_in():
    print_message("To skip press enter")
    sleep()

    check_csv("users.csv")
    users = csv_reader("users.csv", dict=True)

    email_address = user_email_address()
    password = user_password()

    email_exist = False
    password_exist = False

    for user in users:
        if user["email_address"] == email_address:
            email_exist = True
            if user["password"] == password:
                password_exist = True
                break

    if email_exist & password_exist:
        return "logged in"
    elif email_exist & (not password_exist):
        login_error("Incorrect password")
    elif len(email_address) > 1 & (not email_exist):
        login_error("you need to sign up first")
    elif not email_exist:
        print_message("Back to welcome page")


def login_error(warning):
    print_message(Fore.RED + warning)
    print_message("Back to welcome page")


# check if a csv file exist if not then create one


def check_csv(csv_file):
    try:
        csv_reader(csv_file)
    except FileNotFoundError:
        with open(csv_file, "w", newline="") as file:
            csv_writer = csv.writer(file)
            if csv_file == "users.csv":
                csv_writer.writerow(["username", "email_address", "password"])


# list options and features


def make_list():
    list_name = input("It is a list of: ").lower()
    item_header = f"{list_name} list".title()
    csv_file = f"{list_name}.csv"

    print_message("press 'ctrl + c' to quit list")

    # list = [["Index", item_header]]
    list = []
    number = 1

    while True:
        try:
            item = input(f"{number}) ")
            if item:
                list.append({"Index": number, item_header: item})
                # list.append([number, item])
                number += 1
        except KeyboardInterrupt:
            break

    print("")
    # print(list)
    with open(csv_file, "w", newline="") as file:
        csv_writer = csv.DictWriter(file, fieldnames=["Index", item_header])
        # csv_writer = csv.writer(file)
        csv_writer.writeheader()
        for item in list:
            csv_writer.writerow(item)

    get_list(csv_file)


def view_list():
    list_name = input("Name of a list: ").lower()
    csv_file = f"{list_name}.csv"
    get_list(csv_file)


def get_list(csv_file):
    try:
        page(csv_file)
    except:
        print_message(Fore.RED + "There is no such list")


def edit_list():
    list_name = input("Name of a list: ").lower()
    csv_file = f"{list_name}.csv"
    get_list(csv_file)

    # print(list)
    print(Fore.GREEN + "You are now in Editing mode")
    while True:
        list = csv_reader(csv_file)
        print(Fore.GREEN + "Press 'ctrl + c' to exit Editing mode")
        try:
            while True:
                try:
                    row = int(input("row number to modify: "))
                    if 0 < row <= len(list):
                        break
                    else:
                        print(Fore.RED + "choose a valid row number")
                except ValueError:
                    print(Fore.RED + "Input has to be a number")

            data = input("Enter new list data: ")

            with open(csv_file) as file:
                reader = csv.reader(file)
                lines = [row for row in reader]

            if row < len(list):
                lines[row][1] = data
            else:
                lines.append([len(list), data])

            with open(csv_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(lines)

            get_list(csv_file)

        except KeyboardInterrupt:
            print("")
            break


def delete_list():
    list_name = input("Name of a list: ").lower()
    file = f"{list_name}.csv"

    if os.path.exists(file) and os.path.isfile(file):
        os.remove(file)
        print_message(Fore.GREEN + "file successfully deleted")
    else:
        print_message(Fore.RED + "file not found")


# returns lines of csv file in an array depending on argument


def csv_reader(csv_file, dict=False):
    with open(csv_file) as file:
        reader = csv.DictReader(file) if dict else csv.reader(file)
        return [row for row in reader]


# user credentials input and validation
# while loop until satisfied


def user_name():
    while True:
        name = input("your name: ").strip().title()
        if username_validation(name):
            return name
        else:
            print(Fore.RED + NAME_ERR_MSG)


def user_email_address():
    while True:
        email_address = input("your email address: ").strip().lower()
        if email_validation(email_address):
            return email_address
        else:
            print(Fore.RED + EMAIL_ERR_MSG)


def user_password():
    while True:
        password = input("password: ").strip()
        if password_validation(password):
            return password
        else:
            print(Fore.RED + PASSWORD_ERR_MSG)


def username_validation(user):
    match = re.search(NAME_REGEX, user)
    return True if user == "" or match else False


def email_validation(email):
    match = re.search(EMAIL_REGEX, email)
    return True if email == "" or match else False


def password_validation(password):
    match = re.search(PASSWORD_REGEX, password)
    return True if password == "" or match else False


# miscellaneous function


def sleep():
    return time.sleep(0.5)


def print_message(message):
    print(tabulate([[message]], tablefmt="mixed_outline"))
    sleep()


if __name__ == "__main__":
    main()
