# Evaluating retrieval

Fills gap 10 in [Gaps](Gaps.md). The book notes cover [RAGAS](Essential-GraphRAG.md) and
answer quality — context recall, faithfulness, answer correctness — thoroughly. What is
missing is everything *upstream* of the answer.

## Why generation metrics are not enough

A RAG pipeline has two failure modes and one output. When the answer is wrong, it is either
because retrieval did not find the right chunk, or because generation mishandled a chunk it
was given. Answer-level metrics tell you the answer is wrong. They do not tell you which
half to fix, and the fixes are completely different — reranking and chunking on one side,
prompting and model choice on the other.

Measure retrieval on its own, first. It is cheaper (no generation calls), faster, and
deterministic.

## The metrics

Given a query with known-relevant chunks:

| Metric | Question it answers |
| --- | --- |
| **Recall@k** | Of the chunks that should have been found, how many are in the top k? |
| **Precision@k** | Of the top k, how many are actually relevant? |
| **MRR** | How high is the *first* correct result? (1/rank, averaged) |
| **nDCG@k** | Are the good ones near the top? Graded relevance, position-discounted |

**Recall@k is the one to start with**, because it is a ceiling. Anything below it in the
pipeline — reranking, generation — can only work with what retrieval returned. If recall@50
is 0.6, then 40% of your questions are unanswerable no matter how good the reranker is, and
tuning the reranker is wasted effort.

The practical loop this enables: measure recall at a large k (say 50) and at your final k
(say 5). A large gap means **ranking** is your problem, so add a reranker. Both low means
**retrieval** is your problem, so look at chunking, hybrid search, or the embedding model.
That single comparison tells you where to spend the next week.

**nDCG@k** is the one already lurking in the notes — the RavenDB quote in
[Vector Similarity Search](Vector-Similarity-Search.md) mentions nDCG@10 as the standard
benchmark metric. Worth connecting: that is the same measure, and it is what MTEB and BEIR
report.

## The golden dataset is the actual work

Everything above needs labelled data: questions paired with the chunks that should answer
them. There is no shortcut, and this is the part teams skip.

**Start with your five session questions.** They are already written, already
representative, and already cover distinct failure modes. Label which chunks answer each one
and you have the beginning of a real eval set. Say this in the session — it closes the loop
between the demo and the practice.

**Grow it from reality.** Log the questions people actually ask and label a sample weekly.
Real queries are messier than invented ones in ways you will not anticipate: they are
shorter, contain typos, assume context, and ask two things at once.

**LLM-generated questions help you bootstrap** — take a chunk, ask a model to write a
question it answers — but they inherit a bias: they tend to reuse the chunk's own vocabulary,
which makes retrieval look easier than it is. Use them to reach a first fifty, then replace
them with real ones as they arrive.

**Query for the answer, not the value.** The book notes make this point for RAGAS and it
applies here too: an example that asserts "the answer is 7" breaks when someone is hired.
An example that asserts "the answer equals `MATCH (c:Consultant) WHERE ... RETURN count(c)`"
stays correct.

**Cover the negatives.** Include questions the corpus genuinely cannot answer, and check the
system declines rather than confabulates — see [Citations](Citations.md). Also include
greetings and off-topic questions, as the book notes suggest.

Fifty labelled examples is enough to catch regressions. A hundred is enough to make
decisions with. It is far less work than it feels like before you start.

## Beyond the offline set

- **Online signals**: did the user rephrase immediately? Did they click the citation? Both
  are cheap relevance labels that arrive for free.
- **A/B properly.** Retrieval changes interact — hybrid search plus a reranker is not the
  sum of the two individually. Ship one change at a time against the same eval set.
- **LLM-as-judge with care.** Useful for scoring at volume, but judges have known biases
  (position, verbosity, self-preference). Calibrate against human labels on a subset before
  trusting the numbers.

## For the session

Part 8 of the [outline](Session-Outline.md), and the first thing to cut for the 60-minute
version.

If you keep one slide, keep the recall@50-vs-recall@5 diagnostic. It is genuinely
actionable, it takes thirty seconds to explain, and it is the single most useful thing most
teams are not doing.
