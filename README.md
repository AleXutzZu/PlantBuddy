# 🌱 PlantBuddy: Your AI-Powered Plant Care Companion

PlantBuddy is a modern web application designed to instantly provide comprehensive care guides for your houseplants.
Simply upload an image of your plant, and our intelligent backend will identify it and generate a beautifully written,
personalized article on how to keep it thriving.

## Features

* **📷 Image-to-Care Conversion:** Upload a photo and receive an in-depth care article.
* **🌿 AI-Powered Identification:** Uses a fine-tuned **DenseNet CNN** for accurate plant classification.
* **🧠 LLM-Driven Content:** The final article is expertly written by **OpenAI's LLM**.
* **🌐 Comprehensive Information Retrieval:** Combines real-time web searches (via **Tavily**) and curated knowledge from
  a local **LanceDB** vector store to ground the LLM's output.
* **💻 Modern Stack:** Built with a slick **React** and **Tailwind CSS** frontend, powered by a robust **FastAPI**
  backend.
* **⚙️ Advanced Workflow:** Leverages a **LangGraph** pipeline for structured information gathering and
  article generation.

---

## Technical Stack

### Frontend (Client)

| Technology       | Description                                                   |
|:-----------------|:--------------------------------------------------------------|
| **React**        | Fast, component-based user interface.                         |
| **Tailwind CSS** | Utility-first CSS framework for rapid and responsive styling. |

### Backend (Server & AI)

| Technology                            | Description                                                                                              |
|:--------------------------------------|:---------------------------------------------------------------------------------------------------------|
| **FastAPI**                           | High-performance, easy-to-use Python web framework.                                                      |
| **LangGraph**                         | Orchestrates the multi-step AI workflow (prediction, search, retrieval, generation).                     |
| **DenseNet (via PyTorch)**            | Convolutional Neural Network used for initial plant image classification (transfer learning applied).    |
| **Tavily**                            | Tool for real-time, focused web searches to gather current care tips.                                    |
| **LanceDB**                           | Embedded vector database used to store and quickly retrieve curated, high-quality care information.      |
| **OpenAI API**                        | The Large Language Model (LLM) used to structure the web searches and write the final, polished article. |
| **Pydantic**                          | Ensures data validation and structures the JSON output before final article generation.                  |

---

## The LangGraph Workflow

The core logic of PlantBuddy is handled by a sequential LangGraph workflow running on the FastAPI server. This
process is designed to combine the strengths of a classic ML model (for vision) with the retrieval and generation
capabilities of modern LLMs.

1. **Prediction Node (The Predictor):**
    * **Input:** Uploaded plant image.
    * **Action:** Uses the pre-trained **DenseNet CNN** model to classify the plant and output the most likely species
      name.

2. **Web Search Node (Tavily):**
    * **Input:** Plant species name.
    * **Action:** Executes a targeted web search using **Tavily** to gather current and diverse information, especially
      for less common facts or recent tips.

3. **Vector Store Node (LanceDB):**
    * **Input:** Plant species name.
    * **Action:** Performs a similarity search on the local LanceDB vector store to retrieve high-quality,
      pre-vetted care guides and data points (part of a Retrieval-Augmented Generation (RAG) approach).

4. **Structure Node (JSON Formatter):**
    * **Input:** All information from the Prediction, Web Search, and Vector Store nodes.
    * **Action:** Structures all raw information into a standardized JSON format (using a specific Pydantic schema) to
      serve as the context/prompt for the LLM.

5. **Article Generation Node (The Writer - OpenAI LLM):**
    * **Input:** Structured JSON data (The Context).
    * **Action:** Passes the context to the OpenAI LLM (GPT-4o-mini) which writes a complete, well-formatted, and
      user-friendly article on the plant's care, ready to be returned to the user.

---

## Convolutional Neural Network

The CNN model used for prediction is based on the pretrained DenseNet family of models, namely DenseNet169 with about
14M parameters. Using transfer learning, the model was trained on the plants type dataset available
on here [Kaggle](https://www.kaggle.com/datasets/yudhaislamisulistya/plants-type-datasets). It contains 30 classes, each
with
around 1000 images split into train, validation and test sets.

For training the model, the IMAGENET mean and deviation were applied to all images in the preprocessing step, along with
a
resize to 224px and a center crop of the same dimension. The model was trained for 30 epochs, without early-stopping,
on a RX 7700S GPU, using ROCm on Fedora. The table below contains the metrics for a few tested models, for comparison.

| Vision Model | Parameters | Epochs | Accuracy | Precision | Recall | F1  |
|--------------|------------|--------|----------|-----------|--------|-----|
| SimpleCNN    | 8M         | 30     | 80%      | 81%       | 80%    | 80% |
| DenseNet     | 8M         | 20     | 95%      | 95%       | 95%    | 95% |
| DenseNet     | 8M         | 30     | 95%      | 96%       | 95%    | 95% |
| DenseNet     | 14M        | 30     | 96%      | 97%       | 96%    | 96% |

For reference, SimpleCNN is an attempt at building my own CNN based model from scratch, which, all things considered, does not
perform bad as a starting point. However, it does not come close to the accuracy of the pretrained models. Moreover,
we see very slight improvements between different versions of DenseNet, barely 1% of improvement across all metrics.

The greatest challenge in training any of the models was distinguishing between cantaloupes and melons, with most
false-positives being split between these 2 classes. This applies to the largest of the models as well: about 25% of
melons were mis-classified.

---

## Deployment / Running

You can build the image using the provided [Dockerfile](Dockerfile) and run the container. Don't forget to add the
following environment variables:

```dotenv
TAVILY_API_KEY='your Tavily key'
OPENAI_API_KEY='your OpenAI key'
```
