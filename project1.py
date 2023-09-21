from tabulate import tabulate
import sys
import csv
import re
import pyttsx3
from colorama import Fore, init
from multiprocessing import Process
import time
import os


init(autoreset=True)


MENU = [
    ["Main menu"],
    ["1. Make a list"],
    ["2. View a list"],
    ["3. Delete a list"],
    ["4. Exit"],
]

WELCOME = [
    ["Welcome to makelist app"],
    ["1. Sign up or register using email"],
    ["2. Login using email and password"],
    ["3. Exit"],
]

NAME_REGEX = r"^\w{3,}$"
EMAIL_REGEX = r"^\w+\.?\w+@\w+(\.\w{2,3}){1,3}$"
PASSWORD_REGEX = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{4,}$"
NAME_ERR_MSG = "Enter more than 3 character"
EMAIL_ERR_MSG = "Invalid email address"
PASSWORD_ERR_MSG = "minimum 4 characters, 1 uppercase, 1 lowercase and 1 digit"


def main():
    check_csv("welcome.csv")
    check_csv("menu.csv")
    check_csv("users.csv")
    async_python_say("Welcome to makelist app")

    while True:
        # welcome_page
        page("welcome.csv")

        first_option = choose_option(1, 3)
        log_in = match_welcome_option(first_option)

        if log_in:
            print_message(Fore.GREEN + "Successfully " + log_in + " ✅")
            python_say(f"Successfully {log_in}")
        else:
            continue

        while True:
            # main menu
            page("menu.csv")

            menu_option = choose_option(1, 4)
            match_menu_option(menu_option)
            sleep()


# make page


def page(csv_file):
    lines = csv_reader(csv_file)

    print(
        tabulate(
            lines,
            headers="firstrow",
            tablefmt="mixed_outline",
            stralign="center",
        )
    )
    sleep()


# user options


def choose_option(min, max):
    async_python_say("choose an option to continue")

    while True:
        try:
            sleep()
            option = int(input("choose your option: "))
            if validate_option(option, min, max):
                return option
            else:
                async_python_say("choose a valid option")
                print(Fore.RED + "choose from the options given above")
        except ValueError:
            print(Fore.RED + "input has to be a number")
            async_python_say("choose a valid option")


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
            delete_list()
        case _:
            terminate_program()


def terminate_program():
    async_python_say("program terminated")
    print_message(Fore.RED + "programme terminated ❌", border_style="rst")
    sys.exit()


# welcome options
def sign_up():
    print_message("To skip press enter", async_say=True)
    sleep()

    csv_file = "users.csv"

    user_list = csv_reader(csv_file, dict=True)

    username = user_name()
    email_address = user_email_address()
    password = user_password()

    if user_already_exist(email_address):
        print_message(Fore.RED + "user already exists")
        python_say("user already exists")
        return

    user = {"username": username, "email_address": email_address, "password": password}
    if (username == "") or (email_address == "") or (password == ""):
        print_message("Back to welcome page", say=True)
        return

    with open(csv_file, "a", newline="\n") as users:
        writer = csv.DictWriter(
            users, fieldnames=["username", "email_address", "password"]
        )
        writer.writerow(user)

    return "registered"


def user_already_exist(email_address):
    user_list = csv_reader("users.csv", dict=True)
    for user in user_list:
        if user["email_address"] == email_address:
            return True
        else:
            return False


def sign_in():
    print_message("To skip press enter", async_say=True)
    sleep()

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
        print_message("Back to welcome page", say=True)


def login_error(warning):
    print_message(Fore.RED + warning)
    python_say(warning)
    print_message("Back to welcome page", say=True)


# users.csv checker
def check_csv(csv_file):
    try:
        csv_reader(csv_file)
    except FileNotFoundError:
        with open(csv_file, "w", newline="") as file:
            csv_writer = csv.writer(file)
            if csv_file == "users.csv":
                csv_writer.writerow(["username", "email_address", "password"])
            if csv_file == "menu.csv":
                for line in MENU:
                    csv_writer.writerow(line)
            if csv_file == "welcome.csv":
                for line in WELCOME:
                    csv_writer.writerow(line)


# list options
def make_list():
    list_name = input("It is a list of: ").lower()
    csv_file = f"{list_name}.csv"

    item_header = f"{list_name} list"

    print_message("press 'ctrl + c' to quit list", async_say=True)

    list = []
    number = 1

    while True:
        try:
            item = input(f"{number}) ")
            if item:
                list.append({"no": number, item_header: item})
                number += 1
        except KeyboardInterrupt:
            break

    print("")
    if len(list) > 0:
        with open(csv_file, "w", newline="") as file:
            csv_writer = csv.DictWriter(file, fieldnames=["no", item_header])
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
        print_message(Fore.RED + "There is no such file")


def delete_list():
    list_name = input("Name of a list: ").lower()
    file = f"{list_name}.csv"

    if os.path.exists(file) and os.path.isfile(file):
        os.remove(file)
        print_message(Fore.GREEN + "file successfully deleted ✅")
    else:
        print_message(Fore.RED + "file not found ❌")


# csv file reader
def csv_reader(csv_file, dict=False):
    lines = []

    with open(csv_file) as file:
        landing_page = csv.DictReader(file) if dict else csv.reader(file)
        for row in landing_page:
            lines.append(row)

    return lines


# user credentials input and validation


def user_name():
    while True:
        name = input("your name: ").strip().title()
        if username_validation(name):
            return name
        else:
            print(Fore.RED + NAME_ERR_MSG)


def user_email_address():
    while True:
        email_address = input("your email address: ").strip()
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



# pyttsx3
def python_say(message):
    engine = pyttsx3.init()
    engine.setProperty("rate", 180)
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[1].id)
    engine.say(message)
    engine.runAndWait()


# pyttsx3  non blocking
def async_python_say(message):
    p = Process(target=python_say, args=(message,))
    p.start()
    # while p.is_alive():


# miscellaneous function
def sleep():
    return time.sleep(1)


def print_message(message, border_style="mixed_grid", say=False, async_say=False):
    print(tabulate([[message]], tablefmt=border_style))
    if async_say:
        async_python_say(message)
    if say:
        python_say(message)


if __name__ == "__main__":
    main()
