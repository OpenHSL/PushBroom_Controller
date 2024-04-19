import cv2
import os
import sys

from queue import Queue
from PIL import Image
from threading import Thread

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QPixmap

from gui.common_gui import CIU
from gui.mac_micro_gui import Ui_MainWindow
from main import init_hardware
from settings import CameraSettings


shots_buffer = Queue()
sets = CameraSettings()
camera, servomotor = init_hardware()

camera.set_camera_configures(exposure=sets.exposure,
                             gain_value=sets.gain)

servomotor.initialize_pins(direction=sets.direction,
                           mode=sets.mode)


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


class Worker(QObject):
    global camera
    global servomotor
    global shots_buffer
    meta_data = Signal(dict)
    finished_signal = Signal()

    @Slot(dict)
    def do_work(self, meta):
        try:

            camera.set_camera_configures(exposure=meta.exposure,
                                         gain_value=meta.gain)
            servomotor.initialize_pins(direction=meta.direction,
                                       mode=meta.mode)
            save_thread = Thread(target=save_layer,
                                 args=(meta.path_to_save,))

            for i in range(meta.number_of_steps):
                layer = camera.make_shot()
                shots_buffer.put(layer)
                servomotor.next_step()

                if i == 0:
                    save_thread.start()

            save_thread.join()

            self.meta_data.emit({"Status": "Done"})
        except Exception as e:
            self.meta_data.emit({"Status": "Error", "Error": str(e)})

        self.finished_signal.emit()


class MainWindow(CIU):
    meta_requested = Signal(CameraSettings)

    def __init__(self):
        CIU.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        # BUTTONS CONNECTIONS
        self.ui.start_btn.clicked.connect(self.start_record)
        self.ui.preview_btn.clicked.connect(self.make_shot)
        self.ui.image_label.setGeometry(600, 200, 600, 400)

    def make_shot(self):
        global camera

        # camera, _ = init_hardware()

        sets.exposure = int(self.ui.exposure_edit.text())
        sets.gain = int(self.ui.gain_edit.text())

        camera.set_camera_configures(exposure=sets.exposure,
                                     gain_value=sets.gain)

        image = camera.make_shot()
        size_img = (int(image.shape[1] * 0.5),
                    int(image.shape[0] * 0.5))
        image = cv2.resize(image, size_img)

        q_image = self.nparray_2_qimage(image)
        self.ui.image_label.setPixmap(QPixmap(q_image))

    def end_record(self, status):
        if status["Status"] == "Done":
            self.ui.start_btn.setEnabled(True)
        else:
            self.ui.start_btn.setEnabled(True)
            self.show_error(status["Error"])

    def start_record(self):
        self.ui.start_btn.setEnabled(False)

        sets.exposure = int(self.ui.exposure_edit.text())
        sets.gain = int(self.ui.gain_edit.text())
        sets.direction = int(self.ui.direction_edit.text())
        sets.mode = int(self.ui.mode_edit.text())
        sets.number_of_steps = int(self.ui.step_edit.text())

        # THREAD SETUP
        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.meta_data.connect(self.end_record)
        self.meta_requested.connect(self.worker.do_work)

        self.worker.finished_signal.connect(self.worker_thread.quit)
        self.worker.finished_signal.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.meta_requested.emit(sets)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
