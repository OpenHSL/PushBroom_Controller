from pypylon import pylon
import numpy as np

class Basler:
    """
    Class to work with Basler camera

    After calling StartGrabbing all settings of camera will be frozen!

    Attributes
    ----------
    camera : pylon.InstantCamera
        instance of Basler camera from pylon, must be set exposure time for it
    """
    def __init__(self):
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()

    def set_camera_configures(self, exposure: int, gain_value: int = 0):
        """
        sets camera configures

        Parameters
        ----------
        exposure : int
            time of exposure in milliseconds
        gain_value : int
            gain coefficient for shot
        """
        self.camera.ExposureTime.SetValue(exposure)
        self.camera.GainAuto.SetValue('Off')
        self.camera.Gain.SetValue(gain_value)

    def make_shot(self) -> np.array:
        """
        Makes shot from camera and return it as array
        """
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
        grabResult = self.camera.RetrieveResult(9000, pylon.TimeoutHandling_ThrowException)
        while not grabResult.GrabSucceeded():
            grabResult = self.camera.RetrieveResult(9000, pylon.TimeoutHandling_ThrowException)
        self.camera.Close()
        return grabResult.Array

