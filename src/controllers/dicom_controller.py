import logging
from pathlib import Path

import numpy as np
import torch
import yaml
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QGraphicsScene
from qcardia.series import CineSeries
from qcardia_models.models import UNet2d
from skimage.segmentation import mark_boundaries

WANDB_RUN_PATH = Path.cwd() / "wandb"

config_path = WANDB_RUN_PATH / "files" / "config-copy.yaml"
config = yaml.load(Path.open(config_path), Loader=yaml.FullLoader)

the_model = UNet2d(
    nr_input_channels=config["unet"]["nr_image_channels"],
    channels_list=config["unet"]["channels_list"],
    nr_output_classes=config["unet"]["nr_output_classes"],
    nr_output_scales=config["unet"]["nr_output_scales"],
).to("cpu")
model_weights = torch.load(WANDB_RUN_PATH / "files" / "last_model.pt")
the_model.load_state_dict(model_weights)


class DICOMController:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        self.view.load_button_signal.connect(self.load_dicom_files)
        self.view.seg_button_signal.connect(self.run_segmentation)

    def load_dicom_files(self, folder_path):
        self.model.load_dicom_files(folder_path)
        self.cine_seq = CineSeries(Path(folder_path))

        # dicom_files = self.model.dicom_files
        self.display_dicom_images()

    def display_dicom_images(self):

        dicom_data = self.cine_seq.slice_data["slice06"]["pixel_array"][1]

        int_min = 0
        int_max = 1000
        # int_min = dicom_data.WindowCenter - 0.5 * dicom_data.WindowWidth
        # int_max = dicom_data.WindowCenter + 0.5 * dicom_data.WindowWidth
        normalised_array = np.clip(dicom_data, int_min, int_max)
        normalised_array = (
            (normalised_array - int_min) / (int_max - int_min) * 255
        ).astype(np.uint8)

        dicom_scene = QGraphicsScene()
        pixmap = QPixmap.fromImage(
            QImage(
                normalised_array,
                normalised_array.shape[0],
                normalised_array.shape[0],
                QImage.Format_Grayscale8,
            )
        )
        self.normalised_array = normalised_array
        dicom_scene.addPixmap(pixmap)
        self.view.ui.graphicsView.setScene(dicom_scene)

    def run_segmentation(self):
        logging.info("Running segmentation")
        cine_segmentation = self.cine_seq.predict_segmentation(WANDB_RUN_PATH)
        lv_vol_curve = self.cine_seq.compute_volume_curve()
        self.display_segmentation(cine_segmentation, lv_vol_curve)

    def display_segmentation(self, cine_segmentation, lv_vol_curve):

        pixmap = QPixmap.fromImage(
            QImage(
                self.normalised_array,
                self.normalised_array.shape[0],
                self.normalised_array.shape[0],
                QImage.Format_Grayscale8,
            )
        )

        lv = cine_segmentation[5, 1, ...] == 1
        myo = cine_segmentation[5, 1, ...] == 2
        rv = cine_segmentation[5, 1, ...] == 3
        # marked_image = mark_boundaries(np.zeros_like(seg), seg)

        # Find and draw contours
        from cv2 import CHAIN_APPROX_SIMPLE, RETR_EXTERNAL, findContours

        lv_contours, _ = findContours(
            (lv * 255).astype(np.uint8), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE
        )
        myo_contours, _ = findContours(
            (myo * 255).astype(np.uint8), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE
        )
        rv_contours, _ = findContours(
            (rv * 255).astype(np.uint8), RETR_EXTERNAL, CHAIN_APPROX_SIMPLE
        )

        segmentation_scene = QGraphicsScene()
        # pixmap = QPixmap.fromImage(
        #     QImage(
        #         marked_image.data,
        #         seg.shape[0],
        #         seg.shape[1],
        #         QImage.Format_RGB888,
        #     )
        # )

        red = QColor(255, 0, 0)
        green = QColor(0, 255, 0)
        blue = QColor(0, 0, 255)

        painter = QPainter(pixmap)
        for the_contours, the_colour in [
            (lv_contours, red),
            (myo_contours, green),
            (rv_contours, blue),
        ]:
            # Configure contour pen
            pen = QPen(the_colour)
            pen.setWidth(2)
            painter.setPen(pen)
            for contour in the_contours:
                for i in range(len(contour) - 1):
                    painter.drawLine(
                        contour[i][0][0],
                        contour[i][0][1],
                        contour[i + 1][0][0],
                        contour[i + 1][0][1],
                    )
                painter.drawLine(
                    contour[-1][0][0],
                    contour[-1][0][1],
                    contour[0][0][0],
                    contour[0][0][1],
                )

        painter.end()

        segmentation_scene.addPixmap(pixmap)
        self.view.ui.graphicsView.setScene(segmentation_scene)

        from matplotlib import pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

        plot_scene = QGraphicsScene()

        view_rect = self.view.ui.graphicsView_2.viewport().rect()

        # Resize the figure to exactly match the view
        figure, ax = plt.subplots(
            figsize=(
                view_rect.width() / 100,
                view_rect.height() / 100,
            ),  # Initial figsize (will be resized)
            dpi=100,  # High DPI for crisp rendering
            tight_layout=True,  # Automatic layout adjustment
        )

        # Create canvas
        canvas = FigureCanvasQTAgg(figure)
        ax.plot(lv_vol_curve)

        canvas.draw()
        pixmap = canvas.grab()
        plot_scene.addPixmap(pixmap)
        self.view.ui.graphicsView_2.setScene(plot_scene)
