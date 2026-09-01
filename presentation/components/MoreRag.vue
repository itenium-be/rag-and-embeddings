<template>
  <div class="more-rag">

    <div v-for="col in columns" :key="col.name" class="col">
      <div class="col-head">
        <span class="rule" />
        <span class="col-name">{{ col.name }}</span>
      </div>

      <div class="cards reveal" :class="{ shown: clicks >= col.at }">
        <div v-for="c in col.cards" :key="c.topic" class="card">
          <span class="n">{{ c.n }}</span>
          <div class="text">
            <div class="topic">{{ c.topic }}</div>
            <div class="hook">
              <span v-for="(p, i) in parts(c.hook)" :key="i" :class="{ hi: p.hi }">{{ p.t }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="strap reveal" :class="{ shown: clicks >= 2 }">
      None of these are scheduled yet — <b>say which one you want.</b>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// `*...*` marks the numbers this deck already earned: the room recognises them and the
// hook lands without the sentence having to explain itself again.
const parts = (s) =>
  s.split(/(\*[^*]+\*)/).filter(Boolean).map((t) =>
    t.startsWith('*') ? { hi: true, t: t.slice(1, -1) } : { hi: false, t })

const columns = [
  {
    name: 'Answering the ones we could not',
    at: 0,
    cards: [
      { n: 1, topic: 'Text-to-SQL',
        hook: '*Question 5* answered by counting, not by fetching. *Step 6* fakes it' },
      { n: 2, topic: 'GraphRAG',
        hook: 'The other answer to the same question — entities and relationships' },
      { n: 3, topic: 'Router + critic loop',
        hook: 'The fan on the *Retrieval* slide, running: pick, run, check, retry' },
      { n: 4, topic: 'Entity resolution',
        hook: '*36* CV names, *43* HR names, *29* match. Nothing joins until this does' },
    ],
  },
  {
    name: 'Running it for real',
    at: 1,
    cards: [
      { n: 5, topic: 'Access control',
        hook: 'Two people, same question, different chunks. Not theoretical here' },
      { n: 6, topic: 'Real vector stores',
        hook: 'pgvector / Qdrant, HNSW, quantization — *2194* chunks needed none' },
      { n: 7, topic: 'Ingestion at scale',
        hook: 'Tables, OCR, incremental updates, re-embedding on a model swap' },
      { n: 8, topic: 'Cost & latency',
        hook: 'What each of these techniques adds per question' },
    ],
  },
]
</script>

<style scoped>
.more-rag {
  /* rem throughout: the layout's textSize class sets a font-size on the column, and
     em-based sizing here would scale twice. */
  font-size: 1rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0 1.6rem;
  margin-top: 0.9rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts. */
.reveal { opacity: 0; transition: opacity 350ms ease; }
.reveal.shown { opacity: 1; }

.col:nth-child(1) { --accent: var(--color-primary); }
.col:nth-child(2) { --accent: #3f8a46; }

.col-head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.55rem;
}
.rule {
  flex: 0 0 1.5rem;
  height: 3px;
  border-radius: 2px;
  background: var(--accent);
}
.col-name {
  font-family: var(--font-code);
  font-size: 0.78rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #5f6066;
}

.cards { display: flex; flex-direction: column; gap: 0.5rem; }

.card {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  border: 2px solid #a8a8a8;
  border-left: 5px solid var(--accent);
  border-radius: 0 0.5rem 0.5rem 0;
  background: #fefefe;
  padding: 0.5rem 0.85rem;
}
.n {
  flex: 0 0 auto;
  font-family: var(--font-code);
  font-size: 1rem;
  font-weight: 600;
  color: var(--accent);
}
.topic {
  font-family: var(--font-heading);
  font-size: 1.02rem;
  font-weight: 600;
  color: #33343a;
  line-height: 1.15;
}
.hook {
  font-size: 0.82rem;
  line-height: 1.3;
  color: #5f6066;
  margin-top: 0.12rem;
}
.hi {
  color: var(--accent);
  font-weight: 600;
}

.strap {
  grid-column: 1 / -1;
  margin-top: 0.9rem;
  text-align: center;
  font-size: 0.95rem;
  color: #5f6066;
}
.strap b { color: var(--color-primary); }
</style>
