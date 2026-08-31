<template>
  <div class="hybrid">

    <div class="query">
      <span class="q-text">Ik wil AZ-900 halen, wie heeft dat certificaat al?</span>
      <span class="q-fact">5 CVs mention AZ-900</span>
    </div>

    <div class="cols">
      <div v-for="col in columns" :key="col.name" class="col">
        <div class="col-head">
          <span class="col-name">{{ col.name }}</span>
          <span class="col-sub">{{ col.sub }}</span>
        </div>

        <div class="body reveal" :class="{ shown: clicks >= col.at }">
          <div
            v-for="(r, i) in col.rows"
            :key="r.label + i"
            class="row"
            :class="r.hit ? 'hit' : 'miss'"
          >
            <span class="rank">{{ i + 1 }}</span>
            <span class="mark">{{ r.hit ? '✓' : '✗' }}</span>
            <span class="label">
              {{ r.label }}
              <span class="qual">{{ r.qual }}</span>
            </span>
            <span v-if="r.from" class="from">{{ r.from }}</span>
          </div>

          <div class="tally"><b>{{ col.hits }}</b> / 5</div>
        </div>
      </div>
    </div>

    <div class="formula reveal" :class="{ shown: clicks >= 4 }">
      <code>score(chunk) = Σ 1 / (60 + rank)</code>
      <span class="formula-note">decent in both beats first in one</span>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Measured against data/index-real, not assumed: 2194 chunks, the query above, top 5
// per retriever. `from` is the row's rank in the meaning and words lists.
const columns = [
  {
    name: 'MEANING',
    sub: 'vectors',
    at: 1,
    hits: 1,
    rows: [
      { label: 'Igor Romy', qual: 'cv', hit: true },
      { label: 'Gezondheidsverzekering AXA', qual: 'policy · uitgebreide informatie', hit: false },
      { label: 'Credits itenium juni 2025', qual: 'policy', hit: false },
      { label: 'Gezondheidsverzekering AXA', qual: 'policy · onepager', hit: false },
      { label: 'Gezondheidsverzekering AXA', qual: 'policy · presentatie', hit: false },
    ],
  },
  {
    name: 'WORDS',
    sub: 'BM25',
    at: 2,
    hits: 3,
    rows: [
      { label: 'Thomas Janssens', qual: 'credits · Aankoop certificaat', hit: false },
      { label: 'Igor Romy', qual: 'cv', hit: true },
      { label: 'Yannick Manfroy', qual: 'cv', hit: true },
      { label: 'General-Conditions-of-Rental', qual: 'policy · Avis', hit: false },
      { label: 'Jorn Meeusen', qual: 'cv', hit: true },
    ],
  },
  {
    name: 'FUSED',
    sub: 'RRF',
    at: 3,
    hits: 4,
    rows: [
      { label: 'Igor Romy', qual: 'cv', hit: true, from: 'm1 · w2' },
      { label: 'Credits itenium juni 2025', qual: 'policy', hit: false, from: 'm3 · w7' },
      { label: 'Jorn Meeusen', qual: 'cv', hit: true, from: 'm7 · w5' },
      { label: 'Jos Van Loock', qual: 'cv', hit: true, from: 'm12 · w9' },
      { label: 'Mirko Messina', qual: 'cv', hit: true, from: 'm18 · w10' },
    ],
  },
]
</script>

<style scoped>
.hybrid {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  margin-top: 0.7rem;
}

/* Nothing is ever dimmed: unrevealed content is fully transparent and keeps its space,
   so the three columns never reflow as they come in. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.query {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  border-left: 4px solid var(--color-primary);
  background: #ffe2d2;
  border-radius: 0 0.4rem 0.4rem 0;
  padding: 0.55rem 0.9rem;
}
.q-text {
  font-size: 1.15rem;
  color: #8a2f00;
}
.q-fact {
  flex: 0 0 auto;
  font-family: var(--font-code);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: #8a2f00;
}

.cols {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.9rem;
}

.col-head {
  display: flex;
  align-items: baseline;
  gap: 0.45rem;
  padding: 0 0 0.4rem 0.1rem;
  border-bottom: 2px solid #a8a8a8;
  margin-bottom: 0.5rem;
}
.col-name {
  font-family: var(--font-code);
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  color: #343434;
}
.col-sub {
  font-family: var(--font-code);
  font-size: 0.72rem;
  color: #5f6066;
}

.row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-height: 2.7rem;
  border: 2px solid #a8a8a8;
  border-left-width: 5px;
  border-radius: 0.4rem;
  background: #fefefe;
  padding: 0.3rem 0.5rem;
  margin-bottom: 0.4rem;
}
.row.hit { border-left-color: #3f8a46; }
.row.miss { border-left-color: #b23c2c; }

.rank {
  flex: 0 0 auto;
  font-family: var(--font-code);
  font-size: 0.75rem;
  color: #5f6066;
}
.mark {
  flex: 0 0 auto;
  font-size: 0.95rem;
  line-height: 1;
}
.hit .mark { color: #276b2e; }
.miss .mark { color: #b23c2c; }

.label {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  font-size: 0.82rem;
  line-height: 1.15;
  color: #33343a;
}
.qual {
  font-family: var(--font-code);
  font-size: 0.6rem;
  letter-spacing: 0.02em;
  color: #5f6066;
}
.from {
  flex: 0 0 auto;
  font-family: var(--font-code);
  font-size: 0.65rem;
  color: #5f6066;
}

.tally {
  font-family: var(--font-code);
  font-size: 0.95rem;
  text-align: center;
  color: #5f6066;
  padding-top: 0.3rem;
}
.tally b {
  font-size: 1.5rem;
  color: var(--color-primary);
}

.formula {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 1.1rem;
}
.formula code {
  font-family: var(--font-code);
  font-size: 1.05rem;
  color: #343434;
  background: #edf6ee;
  border: 2px solid #3f8a46;
  border-radius: 0.4rem;
  padding: 0.3rem 0.8rem;
}
.formula-note {
  font-size: 0.9rem;
  color: #5f6066;
}
</style>
