<template>
  <div class="scoreboard">

    <div class="head reveal" :class="{ shown: clicks >= 1 }">
      <span class="head-label">naive RAG</span>
    </div>

    <div v-for="(q, i) in asked" :key="q.text" class="row">
      <span class="num">{{ i + 1 }}</span>
      <span class="q">{{ q.text }}</span>
      <span
        class="verdict reveal"
        :class="[q.ok ? 'ok' : 'no', { shown: clicks >= 1 }]"
      >{{ q.ok ? '✓' : '✗' }}</span>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Same five as the use case slide. Kept in step by hand — if one list changes, change
// the other. `ok` is wizard step 1 measured against data/index-real, and it is the same
// verdict `app/questions.yaml` holds and `tests/test_scoreboard.py` asserts.
const asked = [
  { text: 'Welke AI tools mag ik gebruiken?', ok: true },
  { text: 'Ik wil AZ-900 halen, wie heeft dat certificaat al?', ok: false },
  { text: 'Wie kan me helpen met Kubernetes?', ok: false },
  { text: 'Wat zijn de regels rond wagens en laptops?', ok: false },
  { text: 'Hoeveel credits heeft Simon nog?', ok: false },
]
</script>

<style scoped>
.scoreboard { margin-top: 1.4rem; }

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.head {
  display: flex;
  justify-content: flex-end;
  padding: 0 0 0.6rem;
}
.head-label {
  width: 9rem;
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-align: center;
  color: #5f6066;
}

.row {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.75rem 0 0.75rem 1.1rem;
  margin-bottom: 0.85rem;
}
.num {
  flex: 0 0 auto;
  font-family: var(--font-code);
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-primary);
}
.q {
  flex: 1;
  font-size: 1.2rem;
  color: #33343a;
}

/* One column only: the app carries the other five techniques, one at a time. */
.verdict {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  margin: 0 3.5rem;
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
</style>
