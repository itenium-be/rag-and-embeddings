# LinkedIn — post-session

## Post

"Who already holds an AZ-900?"

- Plain vector search found 25% of them. A certificate code is a string, not a meaning — an embedding has nothing to match on.
- BM25 keyword search alongside the embeddings: 75%.
- Reranking the merged results: 100%.

Every technique earns its place, but none of them are free: when we added query rewriting to broaden questions, the one question that had worked from the start — "Which AI tools may I use?" — broke.

The demo app plots our chunks on a map of meaning, and runs every prepared question against a golden dataset. Changing the retrieval pipeline now tells us immediately what we just regressed.

Slides and code in the comments 👇

#RAG #Embeddings #GenAI

## First comment

Slides: https://itenium-be.github.io/Presentations/rag-and-embeddings/
Code: https://github.com/itenium-be/rag-and-embeddings
