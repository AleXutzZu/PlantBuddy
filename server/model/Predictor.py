import torch
from PIL.Image import Image
from torchvision import transforms

from server.model.PlantTypesDenseNetModule import PlantTypesDenseNetLightningModule


class Predictor:
    classes = ['aloevera', 'banana', 'bilimbi', 'cantaloupe', 'cassava', 'coconut', 'corn', 'cucumber', 'curcuma',
               'eggplant', 'galangal', 'ginger', 'guava', 'kale', 'longbeans', 'mango', 'melon', 'orange', 'paddy',
               'papaya', 'peper chili', 'pineapple', 'pomelo', 'shallot', 'soybeans', 'spinach', 'sweet potatoes',
               'tobacco', 'waterapple', 'watermelon']

    def __init__(self):
        self.__device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.__cnn_model = PlantTypesDenseNetLightningModule.load_from_checkpoint("server/plant-types-cnn.ckpt")
        self.__cnn_model.to(self.__device)
        self.__cnn_model.eval()

    def transform_image(self, image: Image):
        imagenet_mean = [0.485, 0.456, 0.406]
        imagenet_std = [0.229, 0.224, 0.225]

        transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=imagenet_mean, std=imagenet_std)
        ])

        batch = transform(image).unsqueeze(0).to(self.__device)
        return batch

    def predict(self, image: Image):
        batch = self.transform_image(image)
        prediction = self.__cnn_model(batch).squeeze(0).softmax(0)

        class_id = prediction.argmax().item()
        score = prediction[class_id].item()
        category_name = Predictor.classes[class_id]
        return category_name, score
