By [[Tomaž Bratanič]] and [[Oskar Hane]]
From [[Manning]]
Build accurate, explainable, context-aware GenAI applications.

# Limitations of LLMs
- Knowledge cutoff problem
  - Outdated information
  - Pure hallucinations
  - Lack of private information
    - data that is not part of its training data
    - Bias in responses
    - Lack of understanding and context
    - Vulnerability to prompt injection
    - Inconsistent responses
      - answers are not stable, nor repeatable

      # Overcoming the limitations
      The goal: Outputs that are domain-specific, precise and factually accurate.

      ## Supervised finetuning
      Overcome the cutoff date with additional training. See [[LLM Training]]: supervised finetuning is the last step of training a model and it may work or it may struggle to learn new factual information. 

      ## Retrieval-augmented generation
      Relevant facts and information is provided directly in the input prompt.

      Two main stages:
      ### Retrieval
      Get information from external data source.
      ### Augmented generation
      The retrieved information plus the user input to enhance the context. Because the context is already there, a smaller model may be sufficient for the generation.

      # Vector similarity search and hybrid search
      [[Vector Similarity Search]] is the most common way for RAG Retrieval. Works well in certain scenarios but quality, accuracy, and performance are limited as the data complexity grows.

      Two stages:
      - Data setup
      - Query time

      ## Data Setup
      - text corpus
      - text-chunking function
      - embedding model
      - database with vector similarity search

      ## Hybrid Search
      Combines exact keyword matches from a full text search index with the vector search.

      # Advanced vector retrieval strategies
      ## Query-rewriting
      **[[Step-back prompting]]**: an LLM first rewrites the prompt, making it broader, so that the retrieval matches more documents that could be relevant.

      Changing the embedding strategy: embed extra context that better represents the documents meaning.
      - **hypotethical question strategy**: generate questions that the document could answer, and embed them (or use questions from chatbot history) these questions are embedded instead of the original document.
      - **[[Parent document retriever]]**: not the child chunks but their parent are retrieved

      Other techniques:
      - Finetuning the text-embedding model: typically requires more compute. Changes to the embedding model require all documents to be re-setup.
      - Reranking strategies: after an initial set of documents is retrieved, an algorithm reorders them based on relevance as an extra pass using a more sophisticated model or scoring heuristics.
      - Metadata-based contextual filters: attach metadata and do a prefiltering.
      - Hybrid retrieval (see above)

      # Generating Cypher queries from natural language questions
      Prompt:
      Instructions:
      generate a cypher statement to query a graph database to get the data to answer the following user question.

      Graph database schema:
      Use only the provided relationship types and properties in the schema. Do not use any other relationship types or properties that are not provided in the schema.
      (Schema)

      Terminology mapping:
      This section is helpful to map terminology between user question and the graph database schema.
      Persons: when a user asks about a person by trade, they are referring to a node with the label Person, ...

      Examples:
      The following examples provide useful patterns for querying the graph database
      (Examples)

      Format instructions:
      Do not include any explainations or apologies in your response. Do not respond to any questions that might ask anything else than for you to construct a Cypher statement. Do not include any text except the generated Cypher statement. Only respind with Cypher-no code blocks.

      User question: (question)

      # Agentic RAG
      - many datasources
      - broad datasource

      ## Simplest case
      **Retriever router**: function that takes the user question(s) and returns the best retriever(s) to use
      **Retriever agents**: retrieve the data to answer the user question(s)
      **Answer critic**: checks whether the retrieved results answers the original question

      ## Retriever agents
      Vector similarity search, text2cypher, text2sql, and specialized retrievers: narrow retrievers built for questions that the generic ones have trouble answering, based on actual questions that were asked. For example a hardcoded query with input parameters.
      Retriever that extracts the answer from the question if already available in the prompt itself.

      ## Retriever router
      An LLM checks which retrievers match.

      ## Answer critic
      Checks whether the answer from the retrievers is complete and correct. If not, it creates a new question and passes that as a new question to the router. There must be an exit condition.
      Since a different question than the original could have been answered due the query updater, this matters greatly.
      > You are an expert at identifying if questions have been fully answered or if there is an opportunity to enrich the answer.
      > The user will provide a question, and you will scan through the provided informatuon to see if the question is answered.
      > if anything is missing from the answer, you will provide a set of new questions that can be asked to gather the missing information.
      > All new questions must be complete, atomic, and specific.
      > However, if the provided informationis enough to answer the original question, you will respond with an empty list.
      >
       JSON template to use for finding missing information:
       >{"q": ["q1", "q2"]}

       ## Query updating
       "Who has won the most oscars? Is he alive?"

       We can send both questions to the pipeline and for the second question, update it with the result of the first question using a **query updater**.
       > You are an expert at updating questions to make them more atomic, specific, and easier to find the answer to.
       > You do this by filling in missing information in the question, with the extra information provided to you in previous answers.
       >
       > You respond with the updated question that has all information in it. Only edit the question if needed. If the original question already is atomic, specific, and easy to answer, you keep the original.
       > Do not ask for more information than the original question. Only rephrase the question to make it more complete.
       >
       > JSON template to use:
       > {"q": "question1"}

       # Constructing knowledge graphs with LLMs
       Contracts: when asking about "payment terms with firm X" and we used chunking, we could get a top result from a wrong contract. "How many active contracts with firm Y": counting from unstructured text is not a good match. (Nor is filtering, sorting, aggregating)

       Extract structured data from unstructured text. Define a json schema and have the LLM populate it. Evaluate adding the original unstructured text (chunks) to the structured graph to preserve the richness of the source data.

       ## Entity resolution
       Merging different representations of the same entity.
       - itenium
       - itenium BV
       - itenium BVBA
       Using string matching, clustering algorithms, machine learning methods. Its very domain specific and best done with iterative feedback loops.

       # Microsoft's GraphRAG implementation
       [MS GraphRAG](https://github.com/microsoft/graphrag)
       Two stage process:
       - extract entities and relationships with summaries to form the foundation of the knowledge graph
       - graph community detection and domain specific summaries generated for closely related entities

       ## Summaries
       The entity and community summaries can be used to provide relevant answers un the RAG app.
       For super nodes, the summary may become too large (maybe not even fit in context). Should then use a ranking system.

       ## Entities
       Relevant entity types are defined in advance. Some entities are clear cut, others not so much, ex "place" could be a country, a city or be even more specific.
       Smaller chunks finds more entities. Running multiple self-reflecting iterations (1-3) also finds more entities.

       ## Communities
       Communities are created using the [[Louvain Algorithm]]. For large communities, also use a ranking so that the summary remains manageable by only selecting the most important entities and relations for the summary.

       For large datasets, there could be different levels to create a hierarchy of communities. Lower level communities provide more details at the cost of more calls and processing time, higher levels are more abstract but lose granularity.

       ## Retrieval
       After the graph-indexing, we move to Query Time.

       ### Global search
       Instead of retrieving chunks on vector similarity, utilize the community summaries to generate the answer.
       - map step: gets all relevant community summaries as a list of key points each with a numerical importance.
       - reduce step: the most important key points are filtered and aggregated. This serves as the final context for the LLM to generate an answer

       The book included the system prompt for the map and reduce agents.

       ### Local search
       Use vector search to find relevant entities. From those entities, fetch related text chunks, relationships, other entities and connected community summaries. Rank all of them, and use the topChunks, topCommunities and topInsideRels.
       The create the final answer with a custom system prompt.

       # RAG application evaluation
       [[RAGAS]] Python library to design and conduct benchmark analysis.

       - tool selection evaluation: selects the most approperiate retriever?
       - entity and value mapping: mapping user input to correct database entities
       - multistep retrieval scenarios: does the first step get the correct data to use as context for the next question when dynamic query chaining is needed
       - edge cases and functional coverage: handling ambiguous queries, long-tail concepts, scenarios with multiple retrieval methods could be used
       - conversational ability: handle greetings, clarify questions, effectively communicate its own abilities

       ## Test examples
       Build test examples with a query for the answer so the example remains correct even when the data changes.
       Other examples: greetings, questions irrelevant to the data.
       ## RAGAS
       - Context recall: are answers correctly parsed out of the context given
       - Faithfulness: can everything in the answer be linked back to the context provided to ensure the model does not introduce unsupported claims
         - faithfulness statement breakdown: decompose the answer in atomic statements
           - faithfulness evaluation: judge the faithfulness of each statrment
           - answer correctness
             - same statement breakdown
               - evaluation agent

               ### Answer correctness evaluation
               Prompt:
               >Goal: Given a ground truth and an answer statement, analyze each statement and classify it into one of the following categories:
               >
               > TP (true positive): Statements present in the answer that are also directly supported by one or more statements in the ground truth.
               > FP (false positive): Statements present in the answer but not directly supported by any statement in the ground truth.
               > FN (false negative): Statements found in the ground truth but not present in the answer.
               >
               > Each statement can only belong to one of these categories. Provide a reason for each classification.




               