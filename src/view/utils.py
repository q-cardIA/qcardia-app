class LayoutParameters:
    def __init__(self) -> None:
        self.spacing = 6  # /3 + /2

        self.large_width = 120  # *2/3
        self.medium_width = (self.large_width * 2 - self.spacing) // 3
        self.small_width = (self.medium_width - self.spacing) // 2

        self.grid_settings_labels_width = 105
        self.transform_button_width = 192
        self.small_label_width = 16

        self.row_height = 28
