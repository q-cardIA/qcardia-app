import logging

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DICOMView(QWidget):
    select_folder_signal = Signal(str)
    segmentation_signal = Signal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.folder_selected = False
        self.folder_label = QLabel("No folder selected.")
        self.layout.addWidget(self.folder_label)

        self.select_folder_button = QPushButton("Select Folder")
        self.layout.addWidget(self.select_folder_button)
        self.select_folder_button.clicked.connect(self.select_folder)

        # Create a separate widget for the image
        self.image_widget = QWidget()
        # Set a layout for the image widget
        self.image_widget.setLayout(QVBoxLayout())
        self.layout.addWidget(self.image_widget)

        # Create separate layout for the segmentation button
        self.segmentation_button_layout = QVBoxLayout()
        # button for running segmentation
        self.segmentation_button = QPushButton("Run Segmentation")
        self.segmentation_button_layout.addWidget(
            self.segmentation_button, alignment=Qt.AlignCenter
        )
        self.layout.addLayout(self.segmentation_button_layout)
        self.segmentation_button.clicked.connect(self.emit_segmentation_signal)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.folder_label.setText(folder_path)
            self.folder_selected = True
            self.select_folder_signal.emit(folder_path)

    def has_folder_been_selected(self):
        return self.folder_selected

    def display_dicom_images(self, dicom_files):
        if not dicom_files:
            logging.info("No DICOM images to display")
            return

        # logging.info(f"Displaying first DICOM image out of {len(dicom_files)}")
        # dicom_data = dicom_files[15]
        dicom_data = dicom_files["slice06"]["pixel_array"][1]
        image_label = QLabel()

        # equalized_array = (
        #     self.histogram_equalization_np(dicom_data.pixel_array.astype(np.float32))
        #     * 255
        # )
        # logging.info(f"Window center: {dicom_data.WindowCenter}")
        # logging.info(f"Window width: {dicom_data.WindowWidth}")

        int_min = 0
        int_max = 1000
        # int_min = dicom_data.WindowCenter - 0.5 * dicom_data.WindowWidth
        # int_max = dicom_data.WindowCenter + 0.5 * dicom_data.WindowWidth
        normalised_array = np.clip(dicom_data, int_min, int_max)
        normalised_array = (
            (normalised_array - int_min) / (int_max - int_min) * 255
        ).astype(np.uint8)

        # normalised_array = np.clip(normalised_array, 0, 255)

        # normalised_array = equalized_array.astype(np.uint8)
        max_index_flat = np.argmax(normalised_array)
        max_position = np.unravel_index(max_index_flat, normalised_array.shape)
        logging.info(f"Type of scaled array: {type(normalised_array)}")
        logging.info(
            f"The minimum pixel value after scaling is {np.min(normalised_array)}"
        )
        logging.info(
            f"The maximum pixel value after scaling is {np.max(normalised_array)} at position {max_position}"
        )
        pixmap = QPixmap.fromImage(
            QImage(
                normalised_array,  # todo: remove again
                normalised_array.shape[0],
                normalised_array.shape[0],
                QImage.Format_Grayscale8,
            )
        )
        image_label = QLabel()
        image_label.setPixmap(pixmap)
        # Add the image label to the image widget
        self.image_widget.layout().addWidget(image_label)

    def emit_segmentation_signal(self):
        if self.has_folder_been_selected():
            self.segmentation_signal.emit()

    def display_segmentation(self, seg_files):
        if self.has_folder_been_selected():
            logging.info("Displaying segmentation")
            dicom_data = seg_files[5, 1, ...]

            # Create an array of the same size as the DICOM image with alternating black and white pixels
            height, width = dicom_data.shape[0], dicom_data.shape[1]

            dicom_array = (50 * dicom_data).astype(np.uint8)

            # Convert the NumPy array to a QImage
            image = QImage(
                dicom_array.data, width, height, width, QImage.Format_Grayscale8
            )

            # Clear the layout
            while self.image_widget.layout().count():
                child = self.image_widget.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Display the image
            pixmap = QPixmap.fromImage(image)
            image_label = QLabel()
            image_label.setPixmap(pixmap)
            self.image_widget.layout().addWidget(image_label)
        else:
            logging.info("No folder selected, cannot display segmentation")
