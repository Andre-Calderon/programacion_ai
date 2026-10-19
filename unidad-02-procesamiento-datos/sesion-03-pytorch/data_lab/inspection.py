"""Load image samples and summarize their labels without training a model."""

import torch
from torch.utils.data import DataLoader, Dataset, Subset
from torchvision.transforms import v2


def image_transform() -> v2.Compose:
    """Convert a PIL image to a float32 image tensor in [0, 1]."""
    return v2.Compose([v2.ToImage(), v2.ToDtype(torch.float32, scale=True)])


def collect_samples(
    dataset: Dataset, limit: int, batch_size: int
) -> tuple[torch.Tensor, torch.Tensor]:
    """Collect the first limit samples, in order, including the last short batch."""
    if limit <= 0 or limit > len(dataset):
        raise ValueError("limit must be between 1 and the dataset length")
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    selected = Subset(dataset, range(limit))
    loader = DataLoader(
        selected,
        batch_size=batch_size,
        shuffle=False,
        drop_last=False,
        num_workers=0,
    )
    image_batches = []
    label_batches = []
    for images, labels in loader:
        image_batches.append(images)
        label_batches.append(labels)
    return torch.cat(image_batches, dim=0), torch.cat(label_batches, dim=0)


def label_summary(
    labels: torch.Tensor, class_names: list[str]
) -> list[dict[str, int | float | str]]:
    """Count each class and report its share of all labels, including empty classes."""
    if labels.ndim != 1 or labels.numel() == 0:
        raise ValueError("Expected a nonempty label vector")
    if labels.dtype != torch.int64:
        raise ValueError("Expected int64 class labels")
    if not class_names or (labels < 0).any() or (labels >= len(class_names)).any():
        raise ValueError("Labels must refer to an existing class")
    counts = torch.bincount(labels, minlength=len(class_names))
    total = labels.numel()
    return [
        {
            "class_id": index,
            "class_name": name,
            "count": int(counts[index]),
            "proportion": int(counts[index]) / total,
        }
        for index, name in enumerate(class_names)
    ]
