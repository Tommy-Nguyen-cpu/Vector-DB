import cohere

def embed_text(api_key : str, text : str):
    co = cohere.ClientV2(api_key=api_key)

    # get the embeddings
    chunks = [text]
    model = "embed-v4.0"
    input_type = "search_query"
    res = co.embed(
        texts=chunks,
        model=model,
        input_type=input_type,
        output_dimension=1024,
        embedding_types=["float"],
    )
    
    return res.embeddings