from Model.Camera import Basler
from Model.HSI import HSImage
from Model.Servomotor import Servomotor
from tqdm import trange
import numpy as np
import os
from PIL import Image

from settings import CameraSettings


def do_step(camera: Basler,
            servomotor: Servomotor,
            path_to_save: str,
            **kwargs):
    """
    Does one step of system concluded shot, adding to hypercube this shot and step of servomotor

    Parameters
    ----------
    camera: Basler
        instance of Basler camera
    hsi: HSImage
        hyperspectral image
    servomotor : Servomotor
        instance of servomotor
    **kwargs concludes
        ind: int
            number of channel of HSI
        num: int
            count of layers (in X-coordinate) in HSI
    """
    ind = kwargs['ind']
    layer = camera.make_shot()
    save_layer(layer=layer, path_to_save=path_to_save, num_step=ind)
    servomotor.next_step()


def save_layer(layer: np.ndarray,
               path_to_save: str,
               num_step: int):
    img = Image.fromarray(layer)
    if not os.path.exists(path_to_save):
        os.mkdir(path_to_save)
    img.save(f"{path_to_save}/frame_{num_step}.png")


def save_hsi(hsi: HSImage,
             path_to_save: str):
    """
    Saves hypespectral image in different formats

    Parameters
    ----------
    hsi: HSImage
        hyperspectral image
    path_to_save: str
        path to saving HSI in format ends with .tiff, .mat, .npy
    """

    if path_to_save.endswith('.mat'):
        hsi.save_to_mat(path_to_file=path_to_save, key='image')
    elif path_to_save.endswith('.tiff'):
        hsi.save_to_tiff(path_to_file=path_to_save)
    elif path_to_save.endswith('.npy'):
        hsi.save_to_npy(path_to_file=path_to_save)
    else:
        print("Saving error: please check file format.\nHSI was not saved")


def start_record():
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

    number_of_steps = CameraSettings.number_of_steps
    exposure = CameraSettings.exposure
    gain_value = CameraSettings.gain
    mode = CameraSettings.mode
    direction = CameraSettings.direction
    path_to_save = CameraSettings.path_to_save

    try:
        camera = Basler()
        camera.set_camera_configures(exposure=exposure, gain_value=gain_value)
        print('Camera initializing successfully')
    except Exception:
        raise "Error camera initializing"

    try:
        servomotor = Servomotor(direction, mode=mode)
        servomotor.initialize_pins()
        print('Servomotor connects successfully')
    except Exception:
        raise "Error with servomotor connections"

    for i in trange(number_of_steps):
        do_step(camera, servomotor, ind=i, path_to_save=path_to_save)

    path_to_log = path_to_save.split('.')[0] + '_log.txt'
    log = f'{number_of_steps}\n' \
          f'{exposure}\n' \
          f'{gain_value}\n' \
          f'{mode}\n' \
          f'{direction}\n' \
          f'{path_to_save}\n' \

    try:
        with open(path_to_log) as f:
            f.write(log)
    except Exception:
        raise "Error with creating log-file"


if __name__ == '__main__':
    start_record()

