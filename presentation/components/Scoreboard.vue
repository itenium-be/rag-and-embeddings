<template>
  <div class="scoreboard">

    <div class="head">
      <span class="head-label mark">naive RAG</span>
      <span class="head-label fix">fixed by</span>
    </div>

    <div v-for="(q, i) in asked" :key="q.text" class="row">
      <span class="num">{{ i + 1 }}</span>
      <span class="q">{{ q.text }}</span>
      <span class="detail reveal" :class="{ shown: clicks >= q.at }">{{ q.detail }}</span>
      <span class="mark">
        <span
          class="verdict reveal"
          :class="[q.ok ? 'ok' : 'no', { shown: clicks >= q.at }]"
        >{{ q.ok ? '✓' : '✗' }}</span>
      </span>
      <span class="fix reveal" :class="{ shown: clicks >= q.at }">{{ q.fix }}</span>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Same five as the use case slide. Kept in step by hand — if one list changes, change
// the other. `ok` and `detail` are wizard step 1 measured against data/index-real; the
// verdicts are the ones `app/questions.yaml` holds and `tests/test_scoreboard.py`
// asserts, and `fix` is the WIZARD_STEPS name of the step that first passes.
const asked = [
  { text: 'Welke AI tools mag ik gebruiken?', ok: true, at: 0, detail: '', fix: '' },
  { text: 'Ik wil AZ-900 halen, wie heeft dat certificaat al?', ok: false, at: 1,
    detail: '1 / 5 holders', fix: 'Hybrid search' },
  { text: 'Wie kan me helpen met Kubernetes?', ok: false, at: 2,
    detail: 'right answer at #3', fix: 'Reranking' },
  { text: 'Wat zijn de regels rond wagens en laptops?', ok: false, at: 3,
    detail: '1 / 5 wagens', fix: 'Query rewriting' },
  { text: 'Hoeveel credits heeft Simon nog?', ok: false, at: 4,
    detail: 'no chunk holds the sum', fix: 'Structure' },
]
</script>

<style scoped>
.scoreboard {
  --mark-col: 4.5rem;
  --fix-col: 9.5rem;
  margin-top: 1.4rem;
}

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
  gap: 1.1rem;
  border: 2px solid transparent;
  padding: 0 0 0.6rem;
}
.head-label {
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  text-align: center;
  color: #5f6066;
}
.head-label.mark { flex: 0 0 var(--mark-col); }
.head-label.fix { flex: 0 0 var(--fix-col); }

.row {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.75rem 0 0.75rem 1.1rem;
  /* The fix column is the last child; its own padding is the row's right edge. */
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

/* The two right-hand columns are fixed width so the head labels sit over them. The head
   carries the row's border as transparent, which is what keeps the two in step. */
.mark { flex: 0 0 var(--mark-col); display: flex; justify-content: center; }
.fix { flex: 0 0 var(--fix-col); text-align: center; }

.detail,
.fix {
  font-family: var(--font-code);
  font-size: 0.72rem;
  line-height: 1.2;
  padding: 0.15rem 0.5rem 0.2rem;
  border-radius: 0.25rem;
}
.detail {
  flex: 0 0 auto;
  background: #e4e4e4;
  color: #5f6066;
}
.fix {
  background: #ffe2d2;
  color: #8a2f00;
}
/* Row 1 has nothing to fix, and an empty chip is still a coloured rectangle. */
.detail:empty,
.fix:empty {
  background: none;
  padding: 0;
}

.verdict {
  flex: 0 0 auto;
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
</style>
