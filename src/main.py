import logging

from PySide6.QtWidgets import QApplication

from controllers.dicom_controller import DICOMController
from model.dicom_model import DICOMModel

# from view.dicom_view import DICOMView
from view.main_window import MainWindow

logging.basicConfig(level=logging.INFO)


def main():
    app = QApplication()
    main_window = MainWindow()

    model = DICOMModel()
    controller = DICOMController(main_window, model)
    main_window.show()
    app.exec_()


if __name__ == "__main__":
    main()
