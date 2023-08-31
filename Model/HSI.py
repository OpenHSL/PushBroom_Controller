import numpy as np
import tifffile as tiff
from scipy.io import loadmat, savemat

class HSImage:
    """
    Hyperspectral Image has dimension X - Y - Z where Z - count of channels

    Attributes
    ----------
    hsi : np.array
        Hyperspectral Image in array format
    coef : np.array
        Matrix of coefficient for normalizing input spectrum if slit has defects

    Methods
    ---------
    TODO write all methods
    """

    def __init__(self,
                 hsi=None,
                 coef=None,
                 conf=None
                 ):
        """
        Parameters
        ----------
        hsi: np.array
            hyperspectral image as numpy array
        coef: np.array
            array of normalize coefficients

        Constants
        ---------
        number_of_channels: int
            number of channels in hyperspectral image

        red_channel: int
            number of red channel in hyperspectral image for color reconstruction
        green_channel: int
            number of green channel in hyperspectral image for color reconstruction
        blue_channel: int
            number of red channel in hyperspectral image for color reconstruction

        gap_coord : int
            it means coordinate of line from diffraction slit
        range_to_spectrum : int
            range from diffraction slit line to area of spectrum
        range_to_end_spectrum : int
            width of spectrum line
        left_bound_spectrum and right_bound spectrum : int
            boundaries of where is spectrum
        """
        self.hsi = hsi
        self.coef = coef

        # initializes constants for cropping hyperspectral area in raw images
        self.conf = conf

        self.number_of_channels = int(conf['HSI']['NUMBER_OF_CHANNELS'])

        self.red_channel = int(conf['HSI']['RED_CHANNEL'])
        self.green_channel = int(conf['HSI']['GREEN_CHANNEL'])
        self.blue_channel = int(conf['HSI']['BLUE_CHANNEL'])

        self.gap_coord = int(conf['HSI']['GAP_COORD'])
        self.range_to_spectrum = int(conf['HSI']['RANGE_TO_SPECTRUM'])
        self.range_to_end_spectrum = int(conf['HSI']['RANGE_TO_END_SPECTRUM'])
        self.left_bound_spectrum = int(conf['HSI']['LEFT_BOUND_SPECTRUM'])
        self.right_bound_spectrum = int(conf['HSI']['RIGHT_BOUND_SPECTRUM'])

    def _coef_norm(self,
                   hs_layer: np.array,
                   thresh=100) -> np.array:
        """
        This method calculates matrix of normalize coefficients from spectrum layer obtained from slit

        Parameters
        ----------
        hs_layer : np.array
            Layer from hyperspectral image obtained from raw slit
        thresh : int
            Value to which whole spectrum will be normalized
        """

        coef = []
        for i in range(self.number_of_channels):
            coef.append([x / thresh for x in hs_layer[:, i]])
        return np.array(coef).T

    def set_coef(self,
                 path_to_norm: str=None,
                 key: str=None):
        """
        This method set coefficients for normalize HSI from file with [.mat, .tiff, .npy] extension

        Parameters
        ----------
        path_to_norm : str
            path to file with raw spectrum obtained from slit
        key : str
            key from .mat file
        """
        temp = None
        if path_to_norm:
            print(f'Hyperspectral image will be normalized with {path_to_norm}')
            if path_to_norm.endswith('.mat') and key:
                temp = loadmat(path_to_norm)[key]
                print(f'Normalizing was successful with {path_to_norm}')
            elif path_to_norm.endswith('.tiff'):
                temp = tiff.imread(path_to_norm)
                print(f'Normalizing was successful with {path_to_norm}')
            elif path_to_norm.endswith('.npy'):
                temp = np.load(path_to_norm)
                print(f'Normalizing was successful with {path_to_norm}')
            else:
                pass
            if temp:
                self.coef = self._coef_norm(temp[:, 5, :])


    def _crop_layer(self, layer: np.array) -> np.array:
        """
        This method crops layer to target area which contain spectrum and return it

        Parameters
        ----------
        layer : np.array
            layer of HSI
        """
        x1 = self.gap_coord + self.range_to_spectrum
        x2 = x1 + self.range_to_end_spectrum
        return layer[x1: x2, self.left_bound_spectrum: self.right_bound_spectrum].T


    def _normalize_spectrum_layer(self,
                                  layer: np.array,
                                  coef=None) -> np.array:
        """
        This method normalizes layer with not uniform light

        Parameters
        ----------
        layer : np.array
            layer of HSI
        coef : np.array
            array of coefficients for uniform light
        """
        return layer / coef if coef else layer

    def _prepare_layer(self, layer: np.array) -> np.array:
        """
        This method crops and normalizes input layer of spectrum and return it

        Parameters
        ----------
        layer : np.array
            layer of HSI
        """
        layer = self._crop_layer(layer)
        layer = self._normalize_spectrum_layer(layer, self.coef)
        return layer

    def add_layer_yz_fast(self,
                          layer: np.array,
                          i: int,
                          count_images: int):
        """
        This method adds layer for X-coordinate with preallocated memory to hyperspectral image

        Parameters
        ----------
        layer : np.array
            layer of HSI
        i : int
            index of current layer
        count_images : int
            length HSI by X-coordinate (count of layers)
        """
        layer = self._prepare_layer(layer)
        if (self.hsi is None):
            x, y, z = count_images, *(layer.shape)
            self.hsi = np.zeros((x, y, z))
        # TODO squeeze
        self.hsi[i, :, :] = layer[None, :, :]

    def add_layer_yz(self, layer: np.array):
        """
        This method adds layer for X-coordinate

        Parameters
        ----------
        layer : np.array
            layer of HSI
        """
        layer = self._prepare_layer(layer)
        if (self.hsi is None):
            self.hsi = layer
        elif (len(np.shape(self.hsi)) < 3):
            self.hsi = np.stack((self.hsi, layer), axis=0)
        else:
            self.hsi = np.append(self.hsi, layer[None, :, :], axis=0)

    def add_layer_xy(self, layer: np.array):
        """
        This method adds layer as image to HSI for Z-coordinate

        Parameters
        ----------
        layer : np.array
            layer of HSI as image
        """
        if (self.hsi is None):
            self.hsi = layer
        elif (len(np.shape(self.hsi)) < 3):
            self.hsi = np.stack((self.hsi, layer), axis=2)
        else:
            self.hsi = np.append(self.hsi, layer[:, :, None], axis=2)

    # TODO make
    def rgb(self) -> np.array:
        """
        This method transforms hyperspectral image to RGB image

        Parameters
        ----------
        channels : tuple[red: int, green: int, blue: int]
            Tuple of numbers of channels accorded to wavelengths of red, green and blue colors
        """
        r, g, b = self.red_channel, self.green_channel, self.blue_channel
        return np.stack((self.hsi[:, :, r], self.hsi[:, :, g], self.hsi[:, :, b]), axis=2)

    def hyp_to_mult(self, number_of_channels: int) -> np.array:
        """
        Converts hyperspectral image to multispectral and return it

        Parameters
        ----------
        number_of_channels : int
            number of channels of multi-spectral image
        """
        if (number_of_channels > np.shape(self.hsi)[2]):
            raise ValueError('Number of MSI is over then HSI')
        MSI = np.zeros((np.shape(self.hsi)[0], np.shape(self.hsi)[1], number_of_channels))
        l = [int(x * (self.number_of_channels / number_of_channels)) for x in range(0, number_of_channels)]
        for k, i in enumerate(l):
            MSI[:, :, k] = self.hsi[:, :, i]

        return MSI

    def get_hsi(self) -> np.array:
        """
        return current hyperspectral image as array
        """
        return self.hsi

    def get_channel(self, number_of_channel: int) -> np.array:
        """
        return channel of hyperspectral image

        Parameters
        ----------
        number_of_channel : int
            number of channel of hyperspectral image
        """
        return self.hsi[:, :, number_of_channel]

    def load_from_array(self, hsi: np.array):
        """
        Initializes hyperspectral image from numpy array

        Parameters
        ----------
        hsi : np.array
            hyperspectral image as array
        """
        self.hsi = hsi

    def load_from_mat(self,
                      path_to_file: str,
                      key: str):
        """
        Initializes hyperspectral image from mat file

        Parameters
        ----------
        path_to_file : str
            path to mat file with HSI
        key : str
            key for dictionary in mat file
        """
        self.hsi = loadmat(path_to_file)[key]

    def save_to_mat(self,
                    path_to_file: str,
                    key: str):
        """
        Saves hyperspectral image to mat file

        Parameters
        ----------
        path_to_file : str
            path to mat file with HSI
        key : str
            key for dictionary in mat file
        """
        # TODO Check values in raw images
        savemat(path_to_file, {key: self.hsi.astype('int16')})

    def load_from_tiff(self, path_to_file: str):
        """
        Initializes hyperspectral image from tiff file

        Parameters
        ----------
        path_to_file : str
            path to tiff file with HSI
        """
        self.hsi = tiff.imread(path_to_file)

    def save_to_tiff(self, path_to_file: str):
        tiff.imwrite(path_to_file, self.hsi)

    def load_from_npy(self, path_to_file: str):
        self.hsi = np.load(path_to_file)

    def save_to_npy(self, path_to_file: str):
        np.save(path_to_file, self.hsi)

