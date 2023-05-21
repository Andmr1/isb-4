import hashlib
import json
import logging
import multiprocessing as mp
from functools import partial
from time import time
from tqdm import tqdm
from matplotlib import pyplot as plt


def check_hash(settings: dict, first_digits: int, other_digits: int) -> int:
    full_number = f'{first_digits}{other_digits}{settings["last_digits"]}'
    if hashlib.sha3_384(f'{full_number}'.encode()).hexdigest() == settings["hash"]:
        logging.info(f'Hash matched! Card number: {full_number}')
        return int(full_number)
    else:
        return False


def find_number(settings: dict, streams: int) -> None:
    completion = False
    with mp.Pool(streams) as pl:
        logging.info(f'Starting card number selection: {settings["first_digits"]}******{settings["last_digits"]}')
        for number in pl.map(partial(check_hash, settings, int(settings["first_digits"])), tqdm(range(100000, 1000000),
                                                                                                colour="#7e42f5")):
            if number:
                pl.terminate()
                completion = True
                data = {}
                data["card_number"] = f'{number}'
                data["Validation_check"] = "Unknown"
                logging.info(f'Card number found! Saving into {settings["save_path"]}')
                try:
                    with open(settings["save_path"], "w") as f:
                        json.dump(data, f)
                except OSError as err:
                    logging.warning(f'{err} during writing to {settings["save_path"]}')
                break
            if completion:
                break
    if completion is not True:
        logging.info("Card nuber not found")


def luhn_algo(settings: dict) -> bool:
    try:
        with open(settings["save_path"], "r") as f:
            data = json.load(f)
    except OSError as err:
        logging.warning(f'{err} during reading from {settings["save_path"]}')
    number = data["card_number"]
    length = len(number)
    if length != 16:
        logging.info("Invalid card number")
        if data["Validation_check"] != "Unknown" or data["Validation_check"] != "Invalid":
            data["Validation_check"] = "Invalid"
            try:
                with open(settings["save_path"], "w") as f:
                    json.dump(data, f)
            except OSError as err:
                logging.warning(f'{err} during writing into {settings["save_path"]}')
        return False
    else:
        s = 0
        for i in range(0, length - 1):
            if(length - i) % 2 == 0:
                if (int(number[i]) * 2) // 10 != 0:
                    s = s + (int(number[i]) * 2) // 10 + (int(number[i]) * 2) % 10
                else:
                    s += (int(number[i]) * 2) // 10
            else:
                s += int(number[i])
        s %= 10
        s %= 10
        s = 10 - s
        if s == int(number[15]):
            logging.info("Card number is valid")
            if data["Validation_check"] != "Unknown" or data["Validation_check"] != "Valid":
                data["Validation_check"] = "Valid"
                try:
                    with open(settings["save_path"], "w") as f:
                        json.dump(data, f)
                except OSError as err:
                    logging.warning(f'{err} during writing into {settings["save_path"]}')
            return True
        else:
            logging.info("Invalid card number")
            if data["Validation_check"] != "Unknown" or data["Validation_check"] != "Invalid":
                data["Validation_check"] = "Invalid"
                try:
                    with open(settings["save_path"], "w") as f:
                        json.dump(data, f)
                except OSError as err:
                    logging.warning(f'{err} during writing into {settings["save_path"]}')
            return False


def make_statistic(settings: dict):
    logging.info("Measuring statistic")
    times = []
    for i in range(int(settings["thread_number"])):
        start = time()
        logging.info(f'Thread number: {i+1}')
        find_number(settings, i+1)
        times.append(time() - start)
    fig = plt.figure(figsize=(30, 5))
    plt.ylabel('Time')
    plt.xlabel('Threads')
    plt.title('Dependence of time on number of threads')
    plt.plot(list(x + 1 for x in range(int(settings["thread_number"]))), times, color='#004158')
    plt.savefig(f'{settings["pic_path"]}')
    logging.info(f'Picture has been saved into {settings["pic_path"]}')


