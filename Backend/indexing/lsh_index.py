from typing import List, Dict, Tuple
import random

from Common.schemas.text_chunk import TextChunk

class LSHIndex:
    """
    Approximate nearest neighbor via random hyperplane locality-sensitive hashing.
    """
    def __init__(self, num_planes: int = 10):
        self.num_planes = num_planes
        self.planes: List[List[float]] = []
        self.buckets: Dict[str, List[Tuple[str, str]]] = {}

        # Will initialize planes when first embedding arrives
    
    def _init_planes(self, dim: int):
        # random hyperplanes with gaussian distribution
        self.planes = [[random.gauss(0,1) for _ in range(dim)] for _ in range(self.num_planes)]

    def _hash(self, emb: List[float]) -> str:
        if not self.planes:
            self._init_planes(len(emb))
        bits = []
        for plane in self.planes:
            dot = sum(e*p for e, p in zip(emb, plane))
            bits.append('1' if dot >= 0 else '0')
        return ''.join(bits)

    def add_chunk(self, doc_id: str, chunk: TextChunk):
        h = self._hash(chunk.embeddings)
        self.buckets.setdefault(h, []).append((doc_id, chunk.id))

    def query_bucket(self, query_emb: List[float]) -> List[Tuple[str, str]]:
        h = self._hash(query_emb)
        return self.buckets.get(h, [])