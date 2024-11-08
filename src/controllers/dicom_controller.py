from pathlib import Path

import torch
import yaml
from qcardia.series import CineSeries
from qcardia_models.models import UNet2d

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

        self.view.select_folder_signal.connect(self.load_dicom_files)
        self.view.segmentation_signal.connect(self.run_segmentation)

    def load_dicom_files(self, folder_path):
        self.model.load_dicom_files(folder_path)
        self.cine_seq = CineSeries(Path(folder_path))

        dicom_files = self.model.dicom_files
        self.view.display_dicom_images(self.cine_seq.slice_data)

    def run_segmentation(self):
        dicom_files = self.model.dicom_files
        cine_segmentation = self.cine_seq.predict_segmentation(WANDB_RUN_PATH)
        print(cine_segmentation.shape)
        self.view.display_segmentation(cine_segmentation)
