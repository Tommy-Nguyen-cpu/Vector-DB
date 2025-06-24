# Vector-DB
## Summary
This repo provides a fast, flexible API for working with text-based data. You’ll find:

* **CRUD & indexing** for libraries, documents and their text “chunks”
* **Instant keyword search** via a simple inverted index
* **Semantic lookup** using Locality-Sensitive Hashing (LSH)
* **Persistent storage** for libraries, docs and chunks (with optional LSH hash persistence later on if preferred)
* **Streamlit demo** to explore and test every feature

Everything you need to add, update, delete, filter and search your text—quickly and reliably.
 
## Installation
The following instructions show how to set up the Vector-DB repository:
1. Pull the Github repository
2. Run "Docker-compose up --build" within the root directory.
3. Go to "[https:127.0.0.1](http://127.0.0.1:8501/)".
4. Wait for the server to start before modifying the "API Base URL" to "http://api:8000".
5. Now you're good to go!

## Technical Choices
The architectural design of our backend was developed with the idea of scalability, maintainability, and extensibility in mind. Specifically:
1. We created a utils file that contains all code that may be used throughout the application/backend for code cleanliness.
2. We store all libraries, documents, and chunks in a local cache during runtime, to reduce the amount of DB calls, since DB calls will introduce overhead.
3. We isolated all library, document, and chunk related DB operations to a "library_data_manager" file, simply because that is best practice; if we decide to deal with more data and of varying types (non-library) in the future, we can essentially create another file for that data, isolating relevant data operations to their own file/class.
4. database_obj may be used across various data managers, so having it be its own class is helpful and scalable in the future.
5. Handlers for indexing and sql operations also ensure we can reduce the amount of code performed directly in the API. This isolates all operations to its own class and allows for scalability (again).
6. Procedure files ensure that, if anything occurs during the SQL operation, we only need to modify one file. Further, this also allows other classes, if needed, to invoke these procedures.

### Indexing vs. LSH
We picked two approaches—simple inverted indexing and byte-optimized LSH—because they offer very different trade-offs. Inverted indexing tokenizes every word, making lookups fast but eating up lots of memory. LSH, by contrast, hashes fixed-size embeddings into buckets, so it uses far less space.

1. **Space complexity**

   * **Inverted index:** O(n × m), where n is the number of chunks and m is the unique tokens.
   * **LSH:** O(p × D + n × k), where p is the number of random hyperplanes, D is the embedding dimension, and k is the average bucket size. In practice, LSH’s footprint is much smaller because it avoids storing every unique token.

2. **Time complexity**

   * **Inverted index:** O(w) per query, with w tokens in the input. Large chunks mean longer lookups.
   * **LSH:** O(p + r), where p hyperplane dot-products filter out most chunks, and r is the few candidates in the resulting buckets. You only compute a handful of dot-products and then scan a small bucket to find the top matches.
