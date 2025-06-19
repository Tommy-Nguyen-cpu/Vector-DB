from typing import List, Dict, Tuple
import random

from Backend.utils.mathUtils import dot_prod
from Common.schemas.text_chunk import TextChunk

class LSHIndex:
    """
    Approximate nearest neighbor via random hyperplane locality-sensitive hashing.
    """
    def __init__(self, num_planes: int = 10):
        self.num_planes = num_planes
        self.planes: List[List[float]] = [] # Holds all embeddings.
        self.buckets: Dict[str, List[Tuple[str, str]]] = {} # Holds mapping between unique bits to ids.

        # Will initialize planes when first embedding arrives
    
    def _init_planes(self, dim: int):
        # random hyperplanes with gaussian distribution
        self.planes = [[random.gauss(0,1) for _ in range(dim)] for _ in range(self.num_planes)]

    def _hash(self, emb: List[float]) -> str:
        if not self.planes:
            self._init_planes(len(emb)) # Initialize random noise for embedding comparison.
        bits = [] # Stores bits, which determines which plane is most similar.
        for plane in self.planes:
            dot = dot_prod(emb, plane) # Finds similarity between each plane and the text embedding.
            bits.append('1' if dot >= 0 else '0')
        return ''.join(bits)

    def add_chunk(self, library_id : str, doc_id: str, chunk: TextChunk):
        h = self._hash(chunk.embeddings)
        self.buckets.setdefault(h, []).append((library_id, doc_id, chunk.id)) # Stores bits as unique identifier in buckets.

    def query_bucket(self, query_emb: List[float]) -> List[Tuple[str, str, str]]:
        h = self._hash(query_emb) # Gets the unique identifier for the bucket.
        return self.buckets.get(h, [])