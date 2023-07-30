"""Containers module."""
from dependency_injector import containers, providers
from .resources_paths import *
from neural_networks.PipelineBasedNeuralNetwork import PipelineBasedNeuralNetwork
from neural_networks.KeywordExtractorNeuralNetwork import KeywordExtractorNeuralNetwork
from transformers import pipeline
from keybert import KeyBERT

# tokenizer_emo_classification_nn_model_path = './NeuralNetworks/t5-base-finetuned-emotion/'
pipeline_emo_classification_nn_model_path = "./NeuralNetworks/emotion-english-distilroberta-base"

# pipeline_emo_classification_nn_model = pipeline("text-classification", model = pipeline_emo_classification_nn_model_path, return_all_scores = True)
pipeline_emo_classification_nn_model = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

kw_model = KeyBERT()

# tokenizer_emo_classification_nn_model = AutoModelWithLMHead.from_pretrained(tokenizer_emo_classification_nn_model_path)
# main_emo_classification_nn_tokenizer = AutoTokenizer.from_pretrained(tokenizer_emo_classification_nn_model_path)

class Container(containers.DeclarativeContainer):
    resources_path = providers.Singleton(
        ResourcesPath,
        pipeline_emo_classification_nn_model_path
    )

    """
    tokenizer_neural_network = providers.Singleton(
        TokenizerBasedNeuralNetwork,
        tokenizer_emo_classification_nn_model,
        main_emo_classification_nn_tokenizer,
    )
    """

    pipeline_neural_network = providers.Singleton(
        PipelineBasedNeuralNetwork,
        pipeline_emo_classification_nn_model
    )

    keyword_extractor_neural_network = providers.Singleton(
        KeywordExtractorNeuralNetwork,
        kw_model
    )
