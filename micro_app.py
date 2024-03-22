import sys
from queue import Queue

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QPixmap

from gui.common_gui import CIU
from gui.mac_micro_gui import Ui_MainWindow
from settings import CameraSettings
import main as controller

sets = CameraSettings()
camera, servomotor = controller.init_hardware()

camera.set_camera_configures(exposure=sets.exposure,
                             gain_value=sets.gain)

servomotor.initialize_pins(direction=sets.direction,
                           mode=sets.mode)


class Worker(QObject):
    global camera
    global servomotor
    meta_data = Signal(dict)

    @Slot(dict)
    def do_work(self, meta):
        try:
            camera.set_camera_configures(exposure=meta.exposure,
                                         gain_value=meta.gain)
            controller.start_record(camera=camera,
                                    servomotor=servomotor,
                                    number_of_steps=meta.number_of_steps,
                                    path_to_save=meta.path_to_save)
            self.meta_data.emit({"Status": "Done"})
        except Exception as e:
            self.meta_data.emit({"Status": "Error", "Error": str(e)})


class MainWindow(CIU):
    meta_requested = Signal(CameraSettings)

    def __init__(self):
        CIU.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        # THREAD SETUP
        self.worker = Worker()
        self.worker_thread = QThread()

        self.worker.meta_data.connect(self.end_record)
        self.meta_requested.connect(self.worker.do_work)

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # BUTTONS CONNECTIONS
        self.ui.start_btn.clicked.connect(self.start_record)
        self.ui.preview_btn.clicked.connect(self.make_shot)

    def make_shot(self):
        global camera

        sets.exposure = int(self.ui.exposure_edit.text())
        sets.gain = int(self.ui.gain_edit.text())

        camera.set_camera_configures(exposure=sets.exposure,
                                     gain_value=sets.gain)

        image = camera.make_shot()
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

        self.meta_requested.emit(sets)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
