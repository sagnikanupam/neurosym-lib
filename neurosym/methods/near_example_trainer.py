from typing import Tuple
import pytorch_lightning as pl
from pytorch_lightning.loggers import CSVLogger
from sklearn.metrics import f1_score, hamming_loss
import torch
from torch import nn
from torch.nn import functional as F
import sys

from neurosym.methods.base_trainer import BaseTrainerConfig, BaseTrainer

class NEARTrainerConfig(BaseTrainerConfig):
    max_seq_len : int = 100
    loss_fn: str = "CrossEntropyLoss"
    num_labels: int = -1 # Set Programmatically
    
class NEARTrainer(BaseTrainer):
    """
    An abstract class that defines the basic functions to 
    implement and train a neural module.
    """

    def __init__(self, model: nn.Module, config : NEARTrainerConfig):
        super().__init__(model=model, config=config)
        assert config.num_labels > 0, "Number of labels must be set programmatically"
        match self.config.loss_fn:
            case 'CrossEntropyLoss':
                self.loss_fn = nn.CrossEntropyLoss()
            case 'BCEWithLogitsLoss':
                self.loss_fn = nn.BCEWithLogitsLoss()
            case 'MSELoss':
                self.loss_fn = nn.MSELoss()
            case _:
                raise NotImplementedError(f"Loss function {self.config.loss_fn} not implemented")

    @staticmethod
    def compute_average_f1_score(predictions: torch.Tensor, targets: torch.Tensor, num_labels: int):
        if num_labels > 1:
            weighted_avg_f1 = 1 - f1_score(targets, predictions, average='weighted')
            unweighted_avg_f1 = 1 - f1_score(targets, predictions, average='macro')
            all_f1 = 1 - f1_score(targets, predictions, average=None)
            return dict(weighted_avg_f1=weighted_avg_f1, unweighted_avg_f1=unweighted_avg_f1, all_f1s=all_f1)
        else:
            avg_f1 = 1 - f1_score(targets, predictions, average='binary')
            all_f1 = 1 - f1_score(targets, predictions, average=None)
            return dict(avg_f1=avg_f1, all_f1s=all_f1)

    @staticmethod
    def label_correctness(predictions: torch.Tensor, targets: torch.Tensor, num_labels: int):
        hamming_accuracy = 1 - hamming_loss(targets.squeeze().cpu(), predictions.squeeze().cpu())
        f1_scores = NEARTrainer.compute_average_f1_score(predictions, targets, num_labels)
        return dict(hamming_accuracy=hamming_accuracy, **f1_scores)

    def loss(self, predictions: torch.Tensor, targets: torch.Tensor) -> dict:
        loss = self.loss_fn(predictions, targets)
        return loss

    def _step(self, inputs, outputs, validation=False, **kwargs):
        predictions = self.model(inputs)
        losses = dict(loss=self.loss(predictions, outputs))

        if validation and self.logger is not None and self.current_epoch % 2 == 0:
            self._log_program_accuracy(predictions, outputs, inputs)

        return losses

    def _log_program_accuracy(self, predictions, outputs, inputs):
        if self.config.num_labels > 1:
            predictions = torch.argmax(predictions, dim=-1)
        else:
            predictions = torch.round(torch.sigmoid(predictions))
        targets = outputs
        correctness = NEARTrainer.label_correctness(predictions, targets, self.config.num_labels)
        self.logger.log_metrics(correctness, step=self.global_step)