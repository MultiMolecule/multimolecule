from __future__ import annotations

import torch
from torch import Tensor, nn
from torch.nn import functional as F

from multimolecule.models.configuration_utils import BaseHeadConfig


class Criterion(nn.Module):

    problem_types = ["regression", "single_label_classification", "multi_label_classification"]

    def __init__(self, config: BaseHeadConfig) -> None:
        super().__init__()
        self.config = config
        self.problem_type = config.problem_type
        self.num_labels = config.num_labels

    def forward(self, logits, labels) -> Tensor | None:
        if labels is None:
            return None
        if self.problem_type is None:
            if self.num_labels == 1:
                self.problem_type = "regression"
            elif self.num_labels > 1 and labels.dtype in (torch.long, torch.int):
                self.problem_type = "single_label_classification"
            else:
                self.problem_type = "multi_label_classification"
            self.config.problem_type = self.problem_type
        if self.problem_type == "regression":
            return (
                F.mse_loss(logits.squeeze(), labels.squeeze()) if self.num_labels == 1 else F.mse_loss(logits, labels)
            )
        if self.problem_type == "single_label_classification":
            return F.cross_entropy(logits.view(-1, self.num_labels), labels.view(-1))
        if self.problem_type == "multi_label_classification":
            return F.binary_cross_entropy_with_logits(logits, labels)
        raise ValueError(f"problem_type should be one of {self.problem_types}, but got {self.problem_type}")
