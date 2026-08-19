# Cypher primer

Fills gap 12 in [Gaps](Gaps.md). [Essential GraphRAG](Essential-GraphRAG.md) hands the
audience a prompt template that *generates* Cypher without ever showing what Cypher looks
like. Two minutes of syntax before that section carries the whole text2cypher demo.

## ASCII art for graphs

The entire idea: a pattern in a `MATCH` clause looks like the thing it matches.

```cypher
(c:Consultant)-[:HAS_SKILL]->(s:Skill)
```

Nodes are in parentheses, relationships in square brackets, arrows show direction. `:Consultant`
and `:Skill` are labels; `HAS_SKILL` is the relationship type. Once people see that the query
is a drawing of the pattern, the rest is detail.

## Enough to read anything

```cypher
MATCH (c:Consultant)-[:HAS_SKILL]->(s:Skill {name: 'Kubernetes'})
WHERE c.available_from <= date('2026-10-01')
RETURN c.name, c.seniority
ORDER BY c.seniority DESC
LIMIT 10
```

`MATCH` finds the pattern, `WHERE` filters, `RETURN` projects. Properties go in braces inside
the pattern or in the `WHERE` clause — `{name: 'Kubernetes'}` and
`WHERE s.name = 'Kubernetes'` do the same thing.

Aggregation needs no `GROUP BY` — it is implied by whatever you also return:

```cypher
MATCH (c:Consultant)-[:HAS_SKILL]->(s:Skill)
RETURN s.name, count(c) AS people
ORDER BY people DESC
```

Variable-length paths are where it beats SQL outright. The org hierarchy from BambooHR,
queried to arbitrary depth:

```cypher
MATCH (manager:Consultant {name: 'X'})<-[:REPORTS_TO*1..]-(report:Consultant)
RETURN report.name
```

`*1..` means "one or more hops". Writing that in SQL means a recursive CTE, and it is the
single most persuasive argument for a graph database — worth showing side by side if you have
a minute.

Optional patterns are `OPTIONAL MATCH`, which behaves like a `LEFT JOIN`. Writing data uses
`CREATE` and `MERGE`, where `MERGE` is get-or-create — the workhorse of graph construction,
and the mechanism behind the entity resolution step in the book notes.

That is genuinely enough to read any query text2cypher will generate.

## Cypher is not Neo4j-only

Worth stating explicitly, because the book notes imply otherwise and the room will assume
vendor lock-in.

Cypher started at Neo4j but was opened as **openCypher** in 2015. It is implemented by
**Memgraph**, **Amazon Neptune**, and **Apache AGE** (a Postgres extension). RedisGraph
spoke it too before being discontinued.

More significantly, **GQL** — ISO/IEC 39075:2024 — is now a real ISO standard, the first new
ISO database language since SQL, and it is heavily derived from Cypher. Neo4j is steering
Cypher toward conformance.

Two practical consequences:

- **text2cypher is a transferable skill**, not a bet on one vendor.
- **Apache AGE makes a Postgres-only demo possible** if you would rather not stand up Neo4j —
  which pairs neatly with the pgvector recommendation in [Vector Stores](Vector-Stores.md).

The caveat is real: dialects differ, so a generated query is not automatically portable, and
most Cypher in the wild still runs on Neo4j. But "you are not locked in" is a fair summary.

## Why this matters for text2cypher

An LLM generating Cypher is only as good as the schema description you give it. The prompt
template in the book notes has a **Graph database schema** section and a **Terminology
mapping** section for good reason: the model needs to know that `HAS_SKILL` exists and that
when a user says "certified in" they mean `HAS_CERTIFICATION`, not `HAS_SKILL`.

Two failure modes to mention:

- **Invented relationships.** The model produces plausible Cypher using a relationship type
  that does not exist. Validate generated queries against the real schema before running
  them, and feed errors back for a retry — this is the single highest-value addition to a
  naive text2cypher implementation.
- **Generated queries are still queries.** Run them read-only, with a timeout and a `LIMIT`.
  A generated traversal with no bound can walk a surprising portion of the graph.

## For the session

Part 6 of the [outline](Session-Outline.md), immediately before the text2cypher demo.

Two slides: the ASCII-art idea, then the variable-length org hierarchy query next to the SQL
recursive CTE it replaces. That contrast does more to explain why the graph half of the
session exists than any amount of prose about knowledge representation.
