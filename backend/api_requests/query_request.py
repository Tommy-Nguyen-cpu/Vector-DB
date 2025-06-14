from pydantic import BaseModel, Field

# TODO: Add query API using this request.
class QueryRequest(BaseModel):
    query: str = Field(..., description="The input text to search for")
    top_k: int = Field(5, description="The number of top similar chunks to return")