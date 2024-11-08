import logging

from PySide6.QtWidgets import QApplication

from controllers.dicom_controller import DICOMController
from model.dicom_model import DICOMModel
from view.dicom_view import DICOMView

logging.basicConfig(level=logging.INFO)


def main():
    app = QApplication([])
    model = DICOMModel()
    view = DICOMView()
    controller = DICOMController(view, model)
    view.show()
    app.exec_()


if __name__ == "__main__":
    main()
