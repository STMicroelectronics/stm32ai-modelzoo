# /*---------------------------------------------------------------------------------------------
#  * Copyright (c) 2025 STMicroelectronics.
#  * All rights reserved.
#  *
#  * This software is licensed under terms that can be found in the LICENSE file in
#  * the root directory of this software component.
#  * If no LICENSE file comes with this software, it is provided AS-IS.
#  *--------------------------------------------------------------------------------------------*/
import torch
import copy
from torch import nn
import torch.nn.functional as F
import torch.distributed as dist

from torch.hub import load_state_dict_from_url

from common.utils import LOGGER
from pathlib import Path
from urllib.parse import urlparse

import requests

def load_pretrained_weights(model, checkpoint_url, device="cpu"):  
    parsed = urlparse(checkpoint_url)

    # Always load from a LOCAL file
    if parsed.scheme in ("http", "https"):
        local_path = _download_checkpoint(checkpoint_url)
    else:
        local_path = Path(checkpoint_url)
        if not local_path.exists():
            raise FileNotFoundError(f"Checkpoint not found at {local_path}")

    # Load checkpoint
    pretrained = torch.load(
        local_path,
        map_location=device,
        weights_only=False,
    )

    if isinstance(pretrained, dict):
        if "state_dict" in pretrained:
            pretrained = pretrained["state_dict"]
        elif "model" in pretrained:
            pretrained = pretrained["model"]

    load_state_dict_partial(model, pretrained)

    print(f"Loaded weights from {local_path}")
    return model


def _download_checkpoint(url: str) -> Path:
    cache_dir = Path.home() / ".cache" / "model_weights"
    cache_dir.mkdir(parents=True, exist_ok=True)

    filename = Path(urlparse(url).path).name
    dst = cache_dir / filename

    if dst.exists():
        return dst

    print(f"Downloading checkpoint from {url}")

    with requests.get(url, stream=True, allow_redirects=True) as r:
        r.raise_for_status()

        # Detect Git LFS pointer (safety check)
        first_chunk = next(r.iter_content(chunk_size=512))
        if b"git-lfs" in first_chunk:
            raise RuntimeError(
                "Downloaded a Git LFS pointer file, not actual weights.\n"
                "Use Git LFS, GitHub Releases, or pre-download the checkpoint."
            )

        with open(dst, "wb") as f:
            f.write(first_chunk)
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return dst

def load_state_dict_partial(model, pretrained_dict):
    """
    Loads matching keys from pretrained_dict into model, ignoring mismatched layers.
    """
    model_dict = model.state_dict()
    matched = {
        k: v
        for k, v in pretrained_dict.items()
        if k in model_dict and v.shape == model_dict[k].shape
    }

    skipped = [k for k in pretrained_dict.keys() if k not in matched]
    model_dict.update(matched)
    model.load_state_dict(model_dict)

    LOGGER.info(
        f"Loaded {len(matched)}/{len(model_dict)} layers from checkpoint. "
        f"Skipped {len(skipped)} layers."
    )


def fuse_blocks(model: torch.nn.Module) -> nn.Module:
    model = copy.deepcopy(model)
    for module in model.modules():
        if hasattr(module, 'fuse'):
            module.fuse()
    return model