from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The input text to search for")
    top_k: int = Field(5, description="The number of top similar chunks to return")