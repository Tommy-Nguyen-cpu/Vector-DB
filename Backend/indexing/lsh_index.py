from typing import List, Dict, Tuple, Set
import random

from utils.mathUtils import dot_prod, cosine_similarity
from Common.schemas.text_chunk import TextChunk

class LSHIndex:
    """
    Approximate nearest neighbor via random hyperplane locality-sensitive hashing.
    """
    def __init__(self, num_planes: int = 3):
        self.num_planes = num_planes
        self.planes: List[List[float]] = [] # Holds all embeddings.
        self.buckets: Dict[str, Set[Tuple[str, str]]] = {} # Holds mapping between unique bits to ids.
        self.docs = set()

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
        self.docs.add(doc_id)
        self.buckets.setdefault(h, set([])).add((library_id, doc_id, chunk.id)) # Stores bits as unique identifier in buckets.

    def query_bucket(self, query_emb: List[float]) -> Set[Tuple[str, str, str]]:
        h = self._hash(query_emb) # Gets the unique identifier for the bucket.
        print(f"Bucket of size: {len(self.buckets)}")
        print(f"Result: {self.buckets.get(h, [])}")
        return self.buckets.get(h, set([]))
    
    def delete_chunk(self, chunk_id : str, embedding : List[float]):
        hash_code = self._hash(embedding)

        if hash_code in self.buckets:
            for _, doc_id, cid in self.buckets[hash_code]:
                if cid == chunk_id:
                    self.docs.remove(doc_id)
                    break

            # Filter bucket, remove any content with the specific chunk id.
            self.buckets[hash_code] = set([(lib, doc, cid)
            for (lib, doc, cid) in self.buckets[hash_code]
            if cid != chunk_id
            ])
        
            self.clean_up(hash_code)
    
    def delete_library(self, library_id : str, embedding : List[float]):
        hash_code = self._hash(embedding)
        if hash_code in self.buckets:
            for lib_id, doc_id, _ in self.buckets[hash_code]:
                if lib_id == library_id:
                    if doc_id in self.docs: self.docs.remove(doc_id)
                    break
            # Filter bucket, remove any content with the specific chunk id.
            self.buckets[hash_code] = [(lib, doc, cid)
            for (lib, doc, cid) in self.buckets[hash_code]
            if lib != library_id
            ]

            self.clean_up(hash_code)

    def clean_up(self, hash_code : str):
        if not self.buckets[hash_code]:
                del self.buckets[hash_code] # Remove any empty buckets.