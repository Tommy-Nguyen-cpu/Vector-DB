import cohere
from sentence_transformers import SentenceTransformer
from abc import ABC, abstractmethod

class BaseEmbedder(ABC):
    def __init__(self, api_key : str = "", model : str = "", input_type : str = ""):
        self.api_key = api_key
        self.model = model
        self.input_type = input_type
    
    @abstractmethod
    def embed(self, texts : list[str]):
        pass

class CohereEmbedder(BaseEmbedder):
    def __init__(self, api_key : str = ""):
        super().__init__(api_key, "embed-v4.0", "search_query")
        self.co = cohere.ClientV2(api_key=self.api_key)
    
    def embed(self, texts : list[str]):
        res = self.co.embed(
        texts=texts,
        model=self.model,
        input_type=self.input_type,
        output_dimension=1024,
        embedding_types=["float"],
        )
    
        return res.embeddings

class SentenceTransformerEmbedder(BaseEmbedder):
    def __init__(self, model = "BAAI/bge-small-en-v1.5"):
        super().__init__(model = model)
        self.encoder = SentenceTransformer(model)
    
    def embed(self, texts : list[str]):
        return self.encoder.encode(texts, normalize_embeddings=True)
