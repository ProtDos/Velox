import base64
import os.path
import socket
import sys
import threading
from datetime import datetime
import time
import csv
import pandas as pd
import hashlib
import string
import shutil

import sqlite3

host = "localhost"
port = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))

server.listen()

clients = []
nicknames = []

dataset = []
form = []

####
clients_asy = []
nicknames_asy = []

dataset_asy = []
form_asy = []
####

private_chats = []

clients__pr = {}
buffer = []

notify_list = []

# Create a separate database connection for each thread
local_data = threading.local()


def get_database_connection():
    # Retrieve the database connection for the current thread
    if not hasattr(local_data, 'connection'):
        local_data.connection = sqlite3.connect('database.db')

        local_data.connection.execute(
            "CREATE TABLE IF NOT EXISTS users(number integer PRIMARY KEY AUTOINCREMENT, username varchar(50) NOT NULL, password varchar(255), id varchar(36))"
        )
        local_data.connection.execute(
            "CREATE TABLE IF NOT EXISTS groups(number integer PRIMARY KEY AUTOINCREMENT, group_name varchar(50) NOT NULL, group_admin varchar(50))"
        )

    return local_data.connection


get_database_connection()


# TODO: Encrypted DB
""" - Chat GPT Example
import sqlite3
from pysqlcipher3 import dbapi2 as sqlcipher
conn = sqlite3.connect('unencrypted.db')
passphrase = 'your_passphrase'  # Make it per input to console and then clear console, so when accessed nobody except himself knows it
conn.executescript(f"ATTACH DATABASE 'encrypted.db' AS encrypted KEY '{passphrase}';")
conn.executescript("SELECT sqlcipher_export('encrypted');")
conn.executescript("DETACH DATABASE encrypted;")
conn.close()

After running this script, you should have an encrypted SQLite database file named 'encrypted.db' containing the data from the 'unencrypted.db' file.

Remember to keep your passphrase secure, as it will be required to access the encrypted database.

"""


def check_username(name):
    every = string.printable[:-6]
    for letter in name:
        if letter not in every:
            return False
    return True


def check_hash(hashed, string):
    salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
    dataBase_password = string + salt
    hashed2 = hashlib.sha256(dataBase_password.encode())
    if hashed == hashed2:
        return True
    return False


def hash_pwd(password):
    salt = "%Up=gJDD8dwL^5+W4pgyprt*sd4QEKTM4nfkD$ZW&Zb_?j^wQUGS6kK?2VkfYy7zu?hnN%a9YU!wduhwnUbKpUe*g*Y#aT$=M2KsA6gMFpU+q!!Ha6HN6_&F3DCL@-gweA47FQyq9wu*yd&By%p-dKPGucfjs2-26He-rPZjLEvBn$a-NFeDHD-UP9A23@5@EtZ5+LmeBS@ZUHW9HDy9U@!3BM2^U5nrq+wUjesgEX^SvDgf8Qs8$kjzEacUGx@r"
    dataBase_password = password + salt
    hashed = hashlib.sha256(dataBase_password.encode())
    return hashed.hexdigest()


def replace_value(old_value, new_value, column_name):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Update the value in the SQLite database
    cursor.execute(f"UPDATE users SET {column_name} = ? WHERE {column_name} = ?",
                   (new_value, old_value))
    con.commit()  # Save the changes


def replace_username_db(username, new_username):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    cursor.execute(f"UPDATE group SET group_admin = ? WHERE group_admin = ?",
                   (new_username, username))
    con.commit()  # Save the changes


def change_password(username, new, by_id=False):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    if by_id:
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new, username))
        con.commit()  # Save the changes
        return
    cursor.execute("UPDATE users SET password = ? WHERE password = ?", (new, username))
    con.commit()  # Save the changes


def check_username_exist(value):
    # Get the database connection for the current thread
    connection = get_database_connection()

    # Create a cursor object for the current thread
    cursor = connection.cursor()
    # Check if the username exists in the SQLite database
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (value,))
    count = cursor.fetchone()[0]
    return count > 0


def is_group_owner(value, group_name):
    # Get the database connection for the current thread
    connection = get_database_connection()

    # Create a cursor object for the current thread
    cursor = connection.cursor()
    # Check if the user is the owner of the group in the SQLite database
    cursor.execute("SELECT COUNT(*) FROM groups WHERE group_admin = ? AND group_name = ?",
                   (value, group_name))
    count = cursor.fetchone()[0]
    return count > 0


def check_group_name_exists(value):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Check if the group name exists in the SQLite database
    cursor.execute("SELECT COUNT(*) FROM groups WHERE group_name = ?", (value,))
    count = cursor.fetchone()[0]
    return count > 0


def check_id_exist(value):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Check if the ID exists in the SQLite database
    cursor.execute("SELECT COUNT(*) FROM users WHERE id = ?", (value,))
    count = cursor.fetchone()[0]
    return count > 0


def get_id(username):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Get the ID for the given username from the SQLite database
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_username(idd):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Get the username for the given ID from the SQLite database
    cursor.execute("SELECT username FROM users WHERE id = ?", (idd,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_password(username):
    # Get the database connection for the current thread
    con = get_database_connection()

    # Create a cursor object for the current thread
    cursor = con.cursor()
    # Get the password for the given username from the SQLite database
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_public(idd):
    try:
        with open(f"public_{idd}.txt", "rb") as file:
            return file.read()
    except:
        return None


def broadcast(message, client):
    try:
        group_id = None
        for item in dataset:
            if item["client"] == client:
                group_id = item["group"]
        if group_id is None:
            print("User not in list")
            pass
        else:
            members = []
            for item in dataset:
                if item["group"] == group_id:
                    members.append(item["client"])
            print(message)
            for person in members:
                if person != client:
                    person.send(message)

    except KeyboardInterrupt:
        pass


def broadcast_asy(message, client, username):
    try:
        group_id = None
        for item in dataset_asy:
            if item["client"] == client:
                group_id = item["group"]
        if group_id is None:
            print("User not in list of asy")
            pass
        else:
            members = []
            for item in dataset_asy:
                if item["group"] == group_id:
                    members.append(item["client"])
            # print(message)
            for person in members:
                if person != client:
                    person.send(username)
                    time.sleep(1)
                    print("asdadasd")
                    person.send(message)

    except KeyboardInterrupt:
        pass


def broadcast_file(name, client, data, sender):
    try:
        print("okay")
        group_id = None
        for item in dataset:
            if item["client"] == client:
                group_id = item["group"]
        if group_id is None:
            print("User not in list")
            pass
        else:
            members = []
            for item in dataset:
                if item["group"] == group_id:
                    members.append(item["client"])
            print("sending file")
            for person in members:
                if person != client:
                    person.send("FILE_INCOMING".encode())
                    time.sleep(.5)
                    person.send(f"{name}".encode())
                    time.sleep(.5)
                    person.send(sender.encode())
                    person.send(data.encode())
                    person.send("DONE:::".encode())

    except KeyboardInterrupt:
        pass


def broadcast_image(name, client, data, sender, final):
    try:
        if not final:
            print("okayx2")
            group_id = None
            for item in dataset:
                if item["client"] == client:
                    group_id = item["group"]
            if group_id is None:
                print("User not in list")
                pass
            else:
                members = []
                for item in dataset:
                    if item["group"] == group_id:
                        members.append(item["client"])
                print("sending image")
                for person in members:
                    if person != client:
                        person.send(f"{name}".encode())
                        time.sleep(.5)
                        person.send(sender.encode())
                        time.sleep(.5)
                        person.send(data)

        else:
            print("okayx3")
            group_id = None
            for item in dataset:
                if item["client"] == client:
                    group_id = item["group"]
            if group_id is None:
                print("User not in list")
                pass
            else:
                members = []
                for item in dataset:
                    if item["group"] == group_id:
                        members.append(item["client"])
                print("sending final message")
                for person in members:
                    person.send("DONE:::".encode())

    except KeyboardInterrupt:
        pass


def handle(client, g_id):
    print("handling")
    dataset.append({"client": client, "group": g_id})
    while True:
        try:
            pp = False
            message = client.recv(1024)
            print(message)

            if message == b'':
                print("cl disconnected ig")
                break
                # pp = True
                # pass
            elif message.decode() == "FILE:::::":
                # TODO: add try-except everywhere
                pp = True
                filename = client.recv(1024).decode()
                sender = client.recv(1024).decode()

                al = []

                while True:
                    more_data = client.recv(1024).decode()
                    if more_data.endswith(":"):
                        more_data = more_data[:-5]
                        al.append(more_data)
                        break
                    else:
                        al.append(more_data)
                    # print(more_data)
                complete_data = "".join(al)
                print("Data received.")
                print(complete_data)

                broadcast_file(name=filename, client=client, data=complete_data, sender=sender)
            elif message.decode() == "IMAGE:::::":
                pp = True
                filename = client.recv(1024)
                sender = client.recv(1024)

                print("okay")
                members = []
                group_id = None
                for item in dataset:
                    if item["client"] == client:
                        group_id = item["group"]
                if group_id is None:
                    print("User not in list")
                    pass
                else:
                    members = []
                    for item in dataset:
                        if item["group"] == group_id:
                            members.append(item["client"])
                    print("sending file")

                print(members)

                for person in members:
                    if person != client:
                        person.send(b"IMAGE_INCOMING")
                        time.sleep(.5)
                        print("sent first")
                        person.send(filename + b"<<MARKER>>" + sender)
                        time.sleep(.5)

                while True:
                    data = client.recv(1024)
                    print("data:", data)
                    if data == b":ENDED:":
                        for person in members:
                            if person != client:
                                person.send(b":ENDED:")
                        break
                    if not data:
                        for person in members:
                            if person != client:
                                person.send(b":ENDED:")
                        break
                    if data.endswith(b":ENDED:"):
                        for person in members:
                            if person != client:
                                person.sendall(data.split(b":ENDED:")[0])
                                time.sleep(.5)
                                person.sendall(b":ENDED:")
                        break

                    for person in members:
                        if person != client:
                            person.sendall(data)
                print("done")
            elif message.decode().startswith(":SCREENSHOT::"):
                print("yes")
                _, name = message.decode().split("::")
                print(f"{name} took a screenshot.")
                pp = True

                for item in form:
                    if item["client"] == client:
                        members = []
                        for item2 in dataset:
                            if item2["group"] == g_id:
                                members.append(item2["client"])
                        for person in members:
                            if person != client:
                                person.send(f":SCREENSHOT::{item['name']}".encode())
                # TODO: Send to every member in group, notify

            if not pp:
                if message.decode() == "PRIV:":
                    print("okay")
                print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Message: ", message)
                if ": " in message.decode():
                    broadcast(message, client)
        except ConnectionResetError:
            try:
                s = False
                for item in form:
                    if item["client"] == client:
                        print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {item['name']} disconnected.")
                        members = []
                        for item2 in dataset:
                            if item2["group"] == g_id:
                                members.append(item2["client"])
                                dataset.remove({"client": client, "group": g_id})
                        for person in members:
                            person.send(f":NEW_LEAVE::{item['name']}".encode())
                        s = True
                if not s:
                    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Unknown client disconnected.")
                clients.remove(client)
                for item in dataset:
                    if item["client"] == client:
                        dataset.remove(item)
            except Exception as e:
                print(e)
                clients.remove(client)
                print("Client disconnected x2")
            break
        except KeyboardInterrupt:
            print("Ctrl+C detected")
            break
        except OSError:
            pass
    # exit("ok")


def handle_asy(client, g_id):
    dataset_asy.append({"client": client, "group": g_id})
    # print(dataset_asy)
    while True:
        try:
            pp = False
            print(dataset_asy)
            username = client.recv(1024)
            if username.startswith(b":SCREENSHOT::"):
                _, name = username.decode().split("::")
                print(f"{name} took a screenshot.")

                for item in form_asy:
                    if item["client"] == client:
                        members = []
                        for item2 in dataset_asy:
                            if item2["group"] == g_id:
                                members.append(item2["client"])
                        for person in members:
                            if person != client:
                                person.send(f":SCREENSHOT::{item['name']}".encode())
            else:
                message = client.recv(1024)

                if message == b'':
                    print("holla")
                    break

                """
                elif message.decode() == "FILE:::::":
                    # TODO: add try-except everywhere
                    pp = True
                    filename = client.recv(1024).decode()
                    sender = client.recv(1024).decode()

                    al = []

                    while True:
                        more_data = client.recv(1024).decode()
                        if more_data.endswith(":"):
                            more_data = more_data[:-5]
                            al.append(more_data)
                            break
                        else:
                            al.append(more_data)
                        # print(more_data)
                    complete_data = "".join(al)
                    print("Data received.")
                    print(complete_data)

                    broadcast_file(name=filename, client=client, data=complete_data, sender=sender)
                elif message.decode() == "IMAGE:::::":
                    pp = True
                    filename = client.recv(1024)
                    sender = client.recv(1024)

                    print("okay")
                    members = []
                    group_id = None
                    for item in dataset:
                        if item["client"] == client:
                            group_id = item["group"]
                    if group_id is None:
                        print("User not in list")
                        pass
                    else:
                        members = []
                        for item in dataset:
                            if item["group"] == group_id:
                                members.append(item["client"])
                        print("sending file")

                    print(members)

                    for person in members:
                        if person != client:
                            person.send(b"IMAGE_INCOMING")
                            time.sleep(.5)
                            print("sent first")
                            person.send(filename + b"<<MARKER>>" + sender)
                            time.sleep(.5)

                    while True:
                        data = client.recv(1024)
                        print("data:", data)
                        if data == b":ENDED:":
                            for person in members:
                                if person != client:
                                    person.send(b":ENDED:")
                            break
                        if not data:
                            for person in members:
                                if person != client:
                                    person.send(b":ENDED:")
                            break
                        if data.endswith(b":ENDED:"):
                            for person in members:
                                if person != client:
                                    person.sendall(data.split(b":ENDED:")[0])
                                    time.sleep(.5)
                                    person.sendall(b":ENDED:")
                            break

                        for person in members:
                            if person != client:
                                person.sendall(data)
                    print("done")
                """

                if not pp:
                    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Message asy: ", message)
                    broadcast_asy(message, client, username)
        except ConnectionResetError:
            try:
                s = False
                for item in form_asy:
                    if item["client"] == client:
                        dataset_asy.remove({"client": client, "group": g_id})
                        print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {item['name']} disconnected.")
                        members = []
                        for item2 in dataset_asy:
                            if item2["group"] == g_id:
                                members.append(item2["client"])
                        for person in members:
                            person.send(
                                f":NEW_LEAVE::{item['name']}::{base64.b64encode(get_public(get_id(item['name']))).decode()}".encode())
                        s = True
                if not s:
                    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Unknown client disconnected.")
                clients_asy.remove(client)
                for item in dataset_asy:
                    if item["client"] == client:
                        dataset_asy.remove(item)
            except Exception as e:
                print(e)
                clients_asy.remove(client)
                print("Client disconnected x2")
            break


def handle_client_while(client, p):
    while True:
        try:
            request = client.recv(1024)
            if request.startswith(b":SCREENSHOT::"):
                _, name, rec = request.decode().split("::")
                print(f"{name} took a screenshot.", rec)
                idd = get_username(rec.replace(" ", "")) + "#" + rec.replace(" ", "")
                recipient_socket = clients__pr[idd]

                recipient_socket.send(f"{name}_took_screenshot::".encode())
                # send_message(rec.replace(" ", ""), f"{name}_took_screenshot::".encode(), p, buf=False)
            else:
                message = client.recv(1024)
                print("Request: ", request)
                print("Message:", message)
                signature = client.recv(1024)
                # print("P:", p)

                request = request.decode()
                if request.startswith("/pm"):
                    _, idd = request.split(" ")
                    send_message(idd, message, p, buf=False, signature=signature)
                else:
                    print("Invalid.")
                    client.close()
                clients__pr[p] = client

        except Exception as e:
            print(e)
            print("client disconnected.")
            break


def handle_client(client, _, oho):
    if oho == "True":
        p = client.recv(1024).decode()
        print(p)
        clients__pr[p] = client
        dd = p
    else:
        clients__pr[oho] = client
        dd = oho
    p = dd
    for item in buffer:
        if item["from"] == p:
            print("yws")
            print("FROM:", item["from"])
            send_message(item["from"], item["mess"], p, buf=True, signature=None)
            buffer.remove(item)
    threading.Thread(target=handle_client_while, args=(client, p,)).start()


def send_notify(to, from_, message):
    print("to:", to)
    to = to.split("#")[1]
    from_ = from_.split("#")[0]

    for item in notify_list:
        if item["id"] == to:
            item["client"].send(f"NOTIFY:{from_}".encode())
            print("yrsefsfsdf")
            time.sleep(.5)
            item["client"].send(message)
            return


def send_message(idd, message, p, buf, signature):
    print(idd, message, p)
    if buf:
        try:
            """
            recipient_socket = clients__pr[idd]
            recipient_socket.send(f"INCOMING:{p}|||".encode())
            print("okay")
            recipient_socket.send(message)
            print("sent")
            """
            recipient_socket = clients__pr[idd]
            print(idd)
            recipient_socket.send(f"INCOMING:{p}|||".encode())
            print("waiting")
            time.sleep(1)
            recipient_socket.send(message)
        except:
            buffer.append({"from": idd, "to": p, "mess": message})
            print("Sender not available.")
            send_notify(idd, p, message)
    else:
        idd = get_username(idd) + "#" + idd
        try:
            recipient_socket = clients__pr[idd]
            print(idd)
            recipient_socket.send(f"{p}---".encode())
            print("waiting x2")
            time.sleep(1)
            recipient_socket.send(message)
            print("waiting x3")
            time.sleep(1)
            recipient_socket.send(signature)
        except Exception as e:
            print(e)
            buffer.append({"from": idd, "to": p, "mess": message, "sign": signature})
            print("Sender not available.")
            send_notify(idd, p, message)


def fuck_around(client, address):
    try:
        xxx = client.recv(1024).decode()
        client.settimeout(None)
        print("X", xxx)
        if xxx == "PRIV:":
            print("private")
            oho = "True"
            client_thread = threading.Thread(target=handle_client, args=(client, address, oho,))
            client_thread.start()
        elif xxx.startswith("SIGNUP:::"):
            print("ye")
            _, username, pas, idd = xxx.split(":::")
            public_key = client.recv(1024).decode()

            if len(username) > 12 or " " in username or not check_username(username):
                client.send(b"errorv3")

            print(username, pas, idd)
            if check_username_exist(username):
                client.send(b"error")
            else:
                if check_id_exist(idd):
                    client.send(b"errorv2")
                else:
                    # Get the database connection for the current thread
                    con = get_database_connection()

                    # Create a cursor object for the current thread
                    cursor = con.cursor()
                    # Insert data into the table
                    cursor.execute("INSERT INTO users (username, password, id) VALUES (?, ?, ?)",
                                   (username, pas, idd))
                    con.commit()
                    with open(f"public_{idd}.txt", "w") as file:
                        file.write(public_key)

                    new_file_path = os.path.join("user_avatars", f"{idd}.jpg")
                    shutil.copy("default.jpg", new_file_path)

                    client.send("success".encode())
        elif xxx.startswith("LOGIN:::"):
            _, username, password = xxx.split(":::")
            print(username, password)
            if not check_username_exist(username):
                client.send("error".encode())
            else:
                pas = get_password(username)
                if pas == password:
                    client.send(f"success:{get_id(username)}".encode())
                else:
                    client.send("errorv2".encode())
        elif xxx.startswith("CHANGE_USERNAME:"):
            _, username, password, new_username = xxx.split(":")
            if not check_username_exist(new_username):
                if check_username_exist(username):
                    pas = get_password(username)
                    if pas == password:
                        replace_value(username, new_username, "username")
                        replace_username_db(username, new_username)
                        client.send(b"success")
                    else:
                        client.send(b"error")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("CHANGE_PASSWORD:"):
            _, old, new, username = xxx.split(":")
            if check_username_exist(username) and get_password(username) == old:
                # replace_value(get_password(username), hash_pwd(new), "password")
                change_password(username, new)
                client.send(b"success")
            else:
                client.send(b"error")
        elif xxx.startswith("DELETE_ALL:"):
            # Get the database connection for the current thread
            con = get_database_connection()

            # Create a cursor object for the current thread
            cursor = con.cursor()
            _, username, password = xxx.split(":")
            if check_username_exist(username):
                pas = get_password(username)
                if pas == password:
                    # Delete a row from the SQLite database
                    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                    con.commit()  # Save the changes
                    client.send(b"success")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("PRIV:"):
            try:
                _, idd = xxx.split(":")
                print("private")
                client_thread = threading.Thread(target=handle_client, args=(client, address, idd,))
                client_thread.start()
            except Exception:
                print("da fuck")
                pass
        elif xxx.startswith("GET_PUBLIC:"):
            idd = xxx.split(":")[1]
            if check_id_exist(idd):
                print("Ok")
                aa = get_public(idd)
                if aa:
                    client.send(aa)
                else:
                    client.send(b"error")
            else:
                print("nah")
                client.send(b"error")
        elif xxx.startswith("GET_USERNAME:"):
            idd = xxx.split(":")[1]
            if check_id_exist(idd):
                aa = get_username(idd)
                if aa:
                    client.send(aa.encode())
                else:
                    client.send(b"error")
            else:
                print("nah")
                client.send(b"error")
        elif xxx.startswith("GET_ID:"):
            username = xxx.split(":")[1]
            aa = get_id(username)
            if aa:
                client.send(aa.encode())
            else:
                client.send(b"error")
        elif xxx.startswith("USER_EXISTS:"):
            u = xxx.split(":")[1]
            if check_username_exist(u):
                client.send(b"exists")
            else:
                client.send(b"not exist")
        elif xxx.startswith("START_VOICE:"):
            print("VOICE REQUEST RECEIVED.")
            threading.Thread(target=start_voice, args=(client,))
        elif xxx.startswith("CREATE_GROUP:"):
            # Get the database connection for the current thread
            con = get_database_connection()

            # Create a cursor object for the current thread
            cursor = con.cursor()
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    client.send(b"group_exists")
                else:
                    # Insert data into the table
                    cursor.execute("INSERT INTO groups (group_name, group_admin) VALUES (?, ?)",
                                   (group_name, username))
                    con.commit()  # Save the changes

                    client.send(b"success")
            else:
                client.send(b"error")
        elif xxx.startswith("VALID_GROUP_NAME:"):
            _, g_name = xxx.split(":")
            if check_group_name_exists(g_name):
                client.send(b"yes")
            else:
                client.send(b"error")
        elif xxx.startswith("DELETE_GROUP:"):
            # Get the database connection for the current thread
            con = get_database_connection()

            # Create a cursor object for the current thread
            cursor = con.cursor()
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    if is_group_owner(username, group_name):
                        # Delete a row from the SQLite database
                        cursor.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
                        con.commit()  # Save the changes

                        client.send(b"success")
                        members = []
                        for item in dataset:
                            if item["group"] == group_name:
                                members.append(item["client"])
                        for person in members:
                            if person != client:
                                person.send(b"::GROUP_DELETION_INITIATED::")
                    else:
                        client.send(b"error")
                else:
                    client.send(b"error")
        elif xxx.startswith("RENAME_GROUP:"):
            # Get the database connection for the current thread
            con = get_database_connection()

            # Create a cursor object for the current thread
            cursor = con.cursor()
            _, group_name, new_group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    if is_group_owner(username, group_name):
                        # Update the group name in the SQLite database
                        cursor.execute("UPDATE groups SET group_name = ? WHERE group_name = ?",
                                       (new_group_name, group_name))
                        con.commit()  # Save the changes

                        client.send(b"success")
                        members = []
                        for item in dataset:
                            if item["group"] == group_name:
                                members.append(item["client"])
                        for person in members:
                            if person != client:
                                person.send(f"::RENAME_OF_GROUP:::{new_group_name}".encode())
                    else:
                        client.send(b"error")
                else:
                    client.send(b"error")
            else:
                client.send(b"error")
        elif xxx.startswith("CREATE_ASY_GROUP:"):
            # Get the database connection for the current thread
            con = get_database_connection()

            # Create a cursor object for the current thread
            cursor = con.cursor()
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                if check_group_name_exists(group_name):
                    client.send(b"group_exists")
                else:
                    # Insert a new row into the SQLite database
                    cursor.execute("INSERT INTO groups (group_name, group_admin) VALUES (?, ?)", (group_name, username))
                    con.commit()  # Save the changes

                    with open(f"groups_asy/{group_name}.csv", "a") as file:
                        file.write(base64.b64encode(get_public(get_id(username))).decode())
                        file.write("\n")
                    client.send(b"success")
            else:
                client.send(b"error")
        elif xxx.startswith("JOIN_ASY_GROUP:"):
            _, group_name, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                with open(f"groups_asy/{group_name}.csv", "a+") as file:
                    s = base64.b64encode(get_public(get_id(username))).decode()
                    if s not in file.read().split("\n"):
                        file.write(s)
                        file.write("\n")
                with open(f"groups_asy/{group_name}.csv", "r") as ff:
                    r = ff.read().split("\n")
                for item in r:
                    print("Sent: ", item)
                    client.send(item.encode())
                time.sleep(0.5)
                print("a")
                client.send(b"success")

                nicknames_asy.append(username)

                clients_asy.append(client)
                form_asy.append({"client": client, "name": username})

                print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {username} joined with asy.")

                members = []
                for item in dataset_asy:
                    if item["group"] == group_name:
                        members.append(item["client"])
                for person in members:
                    # person.settimeout(5)
                    person.send(
                        f":NEW_JOIN::{username}::{base64.b64encode(get_public(get_id(username))).decode()}".encode()
                    )
                    client.send(
                        f":NEW_JOIN2::{base64.b64encode(get_public(get_id(username))).decode()}".encode()
                    )
                    # person.settimeout(None)

                thread = threading.Thread(target=handle_asy, args=(client, group_name,))
                thread.start()

            else:
                client.send(b"error")
        elif xxx.startswith("ID:::::"):
            _, nickname, group_id = xxx.split("|||")
            nicknames.append(nickname)

            clients.append(client)
            form.append({"client": client, "name": nickname})

            print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} {nickname} joined.")

            print("this")

            members = []
            for item in dataset:
                if item["group"] == group_id:
                    members.append(item["client"])
            for person in members:
                print(person)

                person.send(f":NEW_JOIN::{nickname}".encode())

            print("hmm.")

            thread2 = threading.Thread(target=handle, args=(client, group_id,))
            thread2.start()
            print("okay")
        elif xxx.startswith("JOIN_NOTIFY:"):
            _, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                lol = False
                for item in notify_list:
                    if item["id"] == get_id(username):
                        item["client"] = client
                        lol = True
                        break
                if not lol:
                    notify_list.append({"client": client, "id": get_id(username)})
                print(notify_list)
                client.send(b"success")
            else:
                client.send(b"error")
        elif xxx.startswith("CHANGE_AVATAR:"):
            _, username, paswd = xxx.split(":")
            if check_username_exist(username) and get_password(username) == paswd:
                lol = False
                for item in notify_list:
                    if item["id"] == get_id(username):
                        item["client"] = client
                        lol = True
                        break
                if not lol:
                    notify_list.append({"client": client, "id": get_id(username)})
                print(notify_list)
                client.send(b"success")

                file_name = f'user_avatars/{get_id(username)}.jpg'

                # Create a SHA256 hash object
                hash_object = hashlib.sha256()

                with open(file_name, 'wb') as file:
                    while True:
                        data = client.recv(4096)
                        if not data:
                            break

                        # Update the hash object with the received data
                        hash_object.update(data)

                        file.write(data)

                # Calculate the final SHA256 hash
                hash_value = hash_object.hexdigest()
                print("SHA256 hash:", hash_value)

                print(hashlib.sha256(data).hexdigest())

                # Save the received data as an image file

                print("okay")
            else:
                client.send(b"error")
        elif xxx.startswith("GET_AVATAR:"):
            _, username = xxx.split(":")
            with open(f"user_avatars/{get_id(username)}.jpg", 'rb') as file:
                image_data = file.read()
                print(image_data)
                print(hashlib.sha256(image_data).hexdigest())
                client.sendall(image_data)
        else:
            print("Unknown command.")
            client.close()
    except ConnectionResetError:
        pass


########### VOICE CHAT ###########
clients_voice = []
dataset_voice = []


def handle_client_voice(sock, reci):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("nah")
                break

            for item in dataset:
                if item["name"] == reci:
                    item["client"].sendall(data)
        except:
            print("break 1")
            sock.close()
            break
    print("break 2")


def start_voice(client_socket):
    nickname = client_socket.recv(1024).decode()

    for item in dataset:
        if item["name"] == nickname:
            dataset.remove(item)

    rec = client_socket.recv(1024).decode()

    print(f"{nickname} calls {rec}")

    dataset.append({"client": client_socket, "name": nickname})

    # add the client socket to the list
    clients.append(client_socket)

    # handle the client connection in a new thread
    client_thread = threading.Thread(target=handle_client_voice, args=(client_socket, rec,))
    client_thread.start()


def receive():
    print(f"{datetime.now().strftime('[%d-%m-%Y %H:%M:%S]')} Server started...")
    while True:
        try:
            client, address = server.accept()
            print("Connected with {}".format(str(address)))
            client.settimeout(45)

            threading.Thread(target=fuck_around, args=(client, address,)).start()
        except Exception as e:
            print(e)
            print("Client disconnected.")


if __name__ == "__main__":
    receive()
