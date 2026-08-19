LLM Training
============

# Pretraining
Gobble up the entire internet. Requires thousands of GPUs and months of continuous training.

# Supervised finetuning
The model is given high-quality conversations to improve its ability to respond as a helpful assistant. 

# Reward modeling
The model learns what good and bad responses are.

# Reinforcement learning
The model interacts with users or simulated environments and receives feedback to further improve its responses.



Vector Similarity Search
========================

# Vector Index
Not necessary, can also use a brute-force search, but it is highly recommended. A data structure that makes it easy to find similar vectors. Finds the _approximate nearest vectors_, a tradeoff between speed and accuracy.
# Vector Similarity Search Function
Input: a vector
Output: list of vectors

Most common:
- **Cosine similarity**: the angle between two vectors. For text-embeddings: how similar are they in their meaning. Best fit for chatbots.
  - 0 = completely different
    - 1 = identical
    - Euclidean distance: content and intensity of the text

    # Embedding model
    The result of a semantic classification. A necessary step for vector similarity search. Uniform way that captures meaning and context.

    - Embedding: a list of numbers
    - Embedding dimension: the amount of numbers
      - higher dimension = more computationally expensive

      ## Text Chunking
      Smaller chunks improve the retrieval. (Ex: 500 or 2000 characters)
      But there is no one best way: chunk per sentence, paragraph, semantic meaning, ??? Sliding window size or fixed size? How big?
      It depends and not easy to get right.

      ### Contextual embedding
      Each chunk might lose context of the bigger picture it applies to, so this could be added to each chunk.

      ### Overlap
      Have chunks overlap x characters.

      ### Benchmarks
      From [[RavenDB]] by [[Ayende Rahien]]
      > We are using nDCG@10 — normalized Discounted Cumulative Gain at rank 10, the standard retrieval-quality metric on the public BEIR, LoCoV1, and LongEmbed benchmarks.


      Step-back prompting
      ===================

      Transforming a detailed question into a broader, high-level query to reduce the complexity of the vector search process making it easier for the model to identift relevant facts without getting bogged down by the specifics. 

      # Example
      > which team did Thierry Audel play for from 2007 to 2008

      Is broadened to

      > which teams did Thierry Audel play for in his carreer

      # System prompt
      System prompt with [[Few-shot prompting]] examples.

      > You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is easier to answer. Here are a few examples:
      > 
      > input: could the members of the police perform lawful arrests?
      > output: what can the members of the police do?
      >
      > input: Jan Sindel's was born in what country?
      > output: what is Jan Sindel's personal history?

      