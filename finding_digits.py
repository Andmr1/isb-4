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
        logging.info(f'Starting card number selection: {settings["first_digits"]}******{dict["last_digits"]}')
        for number in pl.map(partial(check_hash, settings, int(settings["first_digits"])), tqdm(range(100000, 1000000),
                                                                                                colour="#7e42f5")):
            if number:
                pl.terminate()
                completion = True
                logging.info(f'Card number found! Saving into {settings["save_path"]}')
                try:
                    with open(settings["save_path"], "w") as f:
                        json.dump(number, f)
                except OSError as err:
                    logging.warning(f'{err} during writing to {settings["save_path"]}')
                break
            if completion:
                break
    if completion is not True:
        logging.info("Card nuber not found")
if __name__ == '__main__':
    with open("data/settings.json", "r") as f:
        settings = json.load(f)
    find_number(settings, 6)

