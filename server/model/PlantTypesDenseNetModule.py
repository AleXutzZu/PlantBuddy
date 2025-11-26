import pytorch_lightning as pl
import torch
import torchmetrics
from torchvision.models import densenet169, DenseNet169_Weights


class PlantTypesDenseNetLightningModule(pl.LightningModule):
    def __init__(self, num_classes, learning_rate=1e-3):
        super().__init__()
        self.save_hyperparameters()

        self.model = densenet169(weights=DenseNet169_Weights.DEFAULT)

        for param in self.model.features.parameters():
            param.requires_grad = False

        num_in_features = self.model.classifier.in_features
        self.model.classifier = torch.nn.Linear(num_in_features, num_classes)
        self.loss_fn = torch.nn.CrossEntropyLoss()
        self.accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images)
        loss = self.loss_fn(outputs, labels)

        self.log('train_loss', loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log('train_acc', self.accuracy(outputs, labels), on_step=False, on_epoch=True, prog_bar=True)

        return loss

    def validation_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images)
        loss = self.loss_fn(outputs, labels)

        self.log('val_loss', loss, on_step=False, on_epoch=True, prog_bar=True)
        self.log('val_acc', self.accuracy(outputs, labels), on_step=False, on_epoch=True, prog_bar=True)
        return loss

    def test_step(self, batch, batch_idx):
        images, labels = batch
        outputs = self(images)
        loss = self.loss_fn(outputs, labels)
        self.log('test_loss', loss, on_step=False, on_epoch=True)
        self.log('test_acc', self.accuracy(outputs, labels), on_step=False, on_epoch=True)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.hparams.learning_rate)
