from pathlib import Path
from typing import List, Dict, Tuple

import cv2
import numpy as np
from loguru import logger as _logger
from torch.utils.data import Dataset
from torchvision import transforms


def numeric_sort(array: List[Path]) -> List:
    """
    Accepts a list of paths as argument. Checks whether the filenames are numbered and sorts them numerically.
    If the filenames aren't numbers, sorts them with a default sort.
    :param array:
    :return:
    """
    try:
        array = sorted(array, key=lambda f: int(''.join(filter(str.isdigit, Path(f).stem))))

    except ValueError:
        _logger.info("Cannot sort numerically. Sorting by default")
        array = sorted(array)
    return array


def load_img(img_path: Path) -> np.ndarray:
    """
    Read a image file from disk and return in opencv format.
    :param img_path:
    :return:
    """
    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


class ImagesDataset(Dataset):
    """
    A class that is used to load images from disk.
    """

    def __init__(self, *, image_paths: List[Path], transform=None):
        """
        Initialized with paths to image files and their labels.
        :param image_paths: paths to the images
        :param transform: transformation to apply to the images
        """
        self.image_paths = image_paths
        if transform is None:
            self.transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # imagenet normalization
            ])
        else:
            self.transform = transform
        self.images = None

    def __len__(self) -> int:
        """
        Returns length of the dataset
        :return:
        """
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> Dict:
        image = load_img(self.image_paths[idx])
        image = self.transform(image)

        return image


class FromFolder(ImagesDataset):
    """
    A class that creates a dataset from a directory containing images.
    """

    def __init__(self, folder: Path = "", transform=None,
                 extensions: Tuple[str] = ("*.jpg", "*.png", "*.bmp")):
        image_paths = []
        for extension in extensions:
            image_paths.extend(Path(folder).glob(extension))

        image_paths = numeric_sort(image_paths)

        super().__init__(image_paths=image_paths, transform=transform)
