<template>
  <div class="compound">

    <div class="query">
      <span class="q-text">Wat zijn de regels rond wagens en laptops?</span>
      <span class="q-fact">top 5 chunks per step</span>
    </div>

    <div class="head">
      <span class="h-step">step</span>
      <span class="h-bar">
        <span class="key laptop">laptop policy</span>
        <span class="key car">car policy</span>
        <span class="key other">elsewhere</span>
      </span>
      <span class="h-mark">wagens?</span>
    </div>

    <div v-for="row in steps" :key="row.step" class="row reveal" :class="{ shown: clicks >= row.at }">
      <span class="step">{{ row.step }}</span>
      <span class="bar">
        <span
          v-for="(seg, kind) in { laptop: row.laptop, car: row.car, other: row.other }"
          :key="kind"
          class="seg"
          :class="kind"
          :style="{ flex: seg }"
        >{{ seg || '' }}</span>
      </span>
      <span class="mark">
        <span class="verdict" :class="row.verdict">{{ row.verdict === 'ok' ? '✓' : '✗' }}</span>
      </span>
    </div>

    <div class="rewritten reveal" :class="{ shown: clicks >= 4 }">
      <span class="label">one question in, two questions out</span>
      <code>Wat is het bedrijfswagenbeleid (…)? Wat is het laptop- en IT-materiaalbeleid (…)?</code>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Measured against data/index-real: the five chunks each wizard step retrieves for the
// question above, counted by which document they came from. `other` is the
// arbeidsreglement at step 2 and the Avis rental conditions at step 3 — both plausible
// neighbours of a car policy, neither an answer.
//
// Reranking scoring worse than naive is the point of the row, not a mistake: a
// cross-encoder re-sorts what it is given, and it was given a question about two
// things. Only splitting the question fixes a question that asks for two things.
const steps = [
  { step: 'Naive', at: 0, laptop: 4, car: 1, other: 0, verdict: 'no' },
  { step: 'Hybrid search', at: 1, laptop: 2, car: 2, other: 1, verdict: 'no' },
  { step: 'Reranking', at: 2, laptop: 4, car: 0, other: 1, verdict: 'no' },
  { step: 'Query rewriting', at: 3, laptop: 1, car: 4, other: 0, verdict: 'ok' },
]
</script>

<style scoped>
.compound {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.9rem;
  --step-col: 11rem;
  --mark-col: 5rem;
}

/* Nothing is ever dimmed: unrevealed rows are fully transparent and keep their space,
   so the table never reflows as the steps come in. */
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
  margin-bottom: 0.5rem;
}
.q-text {
  font-size: 1.3rem;
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

.head {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding: 0 1.1rem 0.2rem;
  border: 2px solid transparent;
}
.head span {
  font-family: var(--font-code);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #5f6066;
}
.h-step { flex: 0 0 var(--step-col); }
.h-bar { flex: 1; display: flex; gap: 1.2rem; }
.h-mark { flex: 0 0 var(--mark-col); text-align: center; }

/* The key swatches double as the bar legend, so the colours are never explained twice. */
.key { display: flex; align-items: center; gap: 0.35rem; }
.key::before {
  content: '';
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 0.2rem;
  border: 2px solid #a8a8a8;
}
.key.laptop::before { background: #b9d3ef; border-color: #5c8fc4; }
.key.car::before { background: #ffd4bb; border-color: var(--color-primary); }
.key.other::before { background: #f4f4f4; border-style: dashed; }

.row {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.6rem 1.1rem;
  margin-bottom: 0.5rem;
}
.step {
  flex: 0 0 var(--step-col);
  font-family: var(--font-code);
  font-size: 0.95rem;
  color: #33343a;
}

/* One cell per chunk: the widths are the counts, so "laptops crowded out wagens" is
   readable from the back of the room without doing arithmetic. */
.bar {
  flex: 1;
  display: flex;
  gap: 0.25rem;
  height: 2rem;
}
.seg {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  border-radius: 0.25rem;
  font-family: var(--font-code);
  font-size: 0.9rem;
  overflow: hidden;
}
.seg.laptop { background: #b9d3ef; border-color: #5c8fc4; color: #23405e; }
.seg.car { background: #ffd4bb; border-color: var(--color-primary); color: #8a2f00; }
.seg.other {
  background: #f4f4f4;
  border-color: #a8a8a8;
  border-style: dashed;
  color: #5f6066;
}

.mark { flex: 0 0 var(--mark-col); display: flex; justify-content: center; }
.verdict {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.35rem;
  font-size: 1.2rem;
  line-height: 1;
}
.verdict.ok {
  border-color: #3f8a46;
  background: #edf6ee;
  color: #276b2e;
}
.verdict.no {
  border-color: #b23c2c;
  color: #b23c2c;
}

.rewritten {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-top: 0.4rem;
}
.rewritten .label {
  font-family: var(--font-code);
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #5f6066;
}
.rewritten code {
  font-family: var(--font-code);
  font-size: 0.85rem;
  color: #343434;
  background: #edf6ee;
  border: 2px solid #3f8a46;
  border-radius: 0.4rem;
  padding: 0.4rem 0.8rem;
}
</style>
