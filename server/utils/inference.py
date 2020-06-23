from typing import Optional, Union

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm


def process_dataloader(model, dataloader, input_key: Optional[str] = None,
                       output_key: Optional[Union[str, int]] = None, method: Optional[str] = None,
                       device: str = "cuda"):
    scores = []
    with torch.no_grad():
        model.eval()
        for img in tqdm(dataloader):
            if input_key is not None:
                img = img[input_key]

            img = img.to(device)
            if method is not None:
                output = getattr(model, method)(img)
            else:
                output = model(img)
            if output_key is not None:
                output = output[output_key]

            score = output.tolist()
            scores += score

    return np.array(scores)


def process_dataset(model, dataset, batch_size=8, num_workers=4, device: str = "cuda",
                    input_key: Optional[str] = None,
                    output_key: Optional[Union[str, int]] = None, method: Optional[str] = None):
    dataloader = DataLoader(dataset, batch_size, num_workers=num_workers, shuffle=False)
    scores = process_dataloader(model=model, dataloader=dataloader, input_key=input_key,
                                output_key=output_key, method=method, device=device)
    paths = dataset.image_paths
    p = []
    for path in paths:
        p.append(str(path).split('assets')[1])
    file_inference_results = {"full_path": p, "predicted": list(scores.flatten())}
    # del dataloader,scores
    # print(type(dataset.image_paths))
    # print(type(scores.flatten()))
    return file_inference_results
    # return pd.DataFrame(file_inference_results)
