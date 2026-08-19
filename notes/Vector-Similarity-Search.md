# Vector Similarity Search

## Vector Index
Not necessary, can also use a brute-force search, but it is highly recommended. A data structure that makes it easy to find similar vectors. Finds the _approximate nearest vectors_, a tradeoff between speed and accuracy.

## Vector Similarity Search Function
Input: a vector
Output: list of vectors

Most common:
- **Cosine similarity**: the angle between two vectors. For text-embeddings: how similar are they in their meaning. Best fit for chatbots.
  - 0 = completely different
  - 1 = identical
- **Euclidean distance**: content and intensity of the text

## Embedding model
The result of a semantic classification. A necessary step for vector similarity search. Uniform way that captures meaning and context.

- Embedding: a list of numbers
- Embedding dimension: the amount of numbers
  - higher dimension = more computationally expensive

### Text Chunking
Smaller chunks improve the retrieval. (Ex: 500 or 2000 characters)
But there is no one best way: chunk per sentence, paragraph, semantic meaning, ??? Sliding window size or fixed size? How big?
It depends and not easy to get right.

#### Contextual embedding
Each chunk might lose context of the bigger picture it applies to, so this could be added to each chunk.

#### Overlap
Have chunks overlap x characters.

#### Benchmarks
From [[RavenDB]] by [[Ayende Rahien]]

> We are using nDCG@10 — normalized Discounted Cumulative Gain at rank 10, the standard retrieval-quality metric on the public BEIR, LoCoV1, and LongEmbed benchmarks.
