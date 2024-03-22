from Model.Camera import Basler
from Model.Servomotor import Servomotor
from tqdm import trange
from queue import Queue
from threading import Thread
import numpy as np
import os
from PIL import Image

from settings import CameraSettings


shots_buffer = Queue()
sets = CameraSettings()


def save_layer(path_to_save: str):
    global shots_buffer
    counter = 0
    while shots_buffer.qsize() > 0:
        layer = shots_buffer.get()
        img = Image.fromarray(layer)
        if not os.path.exists(path_to_save):
            os.mkdir(path_to_save)
        img.save(f"{path_to_save}/frame_{counter}.png")
        counter += 1


def do_step(camera: Basler,
            servomotor: Servomotor):
    """
    Does one step of system concluded shot, adding to hypercube this shot and step of servomotor

    Parameters
    ----------
    camera: Basler
        instance of Basler camera
    servomotor : Servomotor
        instance of servomotor
    """
    layer = camera.make_shot()
    shots_buffer.put(layer)
    servomotor.next_step()


def init_hardware():
    try:
        camera = Basler()
        print('Camera initializing successfully')
    except:
        raise

    try:
        servomotor = Servomotor()
        print('Servomotor connects successfully')
    except:
        raise

    return camera, servomotor


def start_record(camera,
                 servomotor,
                 number_of_steps,
                 path_to_save: str):
    """
    Starts recording of hyperspectral image

    Parameters
    ----------
    number_of_steps: int
        count of layers (images) of hyperspectral image which will shouted
    exposure: int
        time of exposure in milliseconds
    mode: int
        mode for servomotor
    velocity: int
        velocity of servomotor
    direction: int
        get 1 or 0 values
    path_to_save: str
        path to mat file in which hyperspepctral image will be saved
    path_to_coef: str
        path to file with raw spectrum obtained from slit
    key_coef: str
        key for mat file of matrix of normalized coefficients
    """

    print('Start recording...')

    save_thread = Thread(target=save_layer,
                         args=(path_to_save,))

    for i in trange(number_of_steps):
        do_step(camera=camera,
                servomotor=servomotor)

        if i == 0:
            save_thread.start()

    save_thread.join()
    print(f'End saving shots to {path_to_save}')


def save_logs():

    path_to_log = sets.path_to_save.split('.')[0] + '_log.txt'
    log = f'number_of_steps: {sets.number_of_steps}\n' \
          f'exposure: {sets.exposure}\n' \
          f'gain: {sets.gain}\n' \
          f'mode: {sets.mode}\n' \
          f'direction: {sets.direction}\n' \
          f'path_to_save: {sets.path_to_save}\n'

    try:
        with open(path_to_log, 'w') as f:
            f.write(log)
    except Exception:
        raise "Error with creating log-file"


if __name__ == '__main__':
    camera, servomotor = init_hardware()

    camera.set_camera_configures(exposure=sets.exposure,
                                 gain_value=sets.gain)

    servomotor.initialize_pins(direction=sets.direction,
                               mode=sets.mode)

    start_record(camera=camera,
                 servomotor=servomotor,
                 number_of_steps=sets.number_of_steps,
                 path_to_save=sets.path_to_save)

    save_logs()
