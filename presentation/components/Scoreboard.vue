<template>
  <div class="scoreboard">

    <div class="head">
      <span class="head-label mark"></span>
      <span class="head-label fix">techniques</span>
    </div>

    <div v-for="q in asked" :key="q.text" class="row">
      <span class="num">{{ q.n }}</span>
      <span class="q">{{ q.text }}</span>
      <div class="stages">
        <div
          v-for="st in q.stages"
          :key="st.fix"
          class="stage reveal"
          :class="{ shown: clicks >= st.at }"
        >
          <span class="detail">{{ st.detail }}</span>
          <span class="mark">
            <span class="verdict" :class="st.verdict">{{ MARK[st.verdict] }}</span>
          </span>
          <span class="fix">{{ st.fix }}</span>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  clicks: { type: Number, default: 0 },
  // Which questions this instance renders, by their number. The four are split over
  // three slides and keep their numbering, so the number cannot come from the loop.
  show: { type: Array, default: null },
})

const MARK = { ok: '✓', part: '!', no: '✗' }

// Same four as the use case slide. Kept in step by hand — if one list changes, change
// the other. Every verdict and count below is one `app/questions.yaml` holds and
// `tests/test_scoreboard.py` asserts against data/index-real, and `fix` names the
// WIZARD_STEPS step it belongs to.
//
// AZ-900 gets three stages because it is the one question two techniques share: no
// amount of fusion tuning reaches Yannick Manfroy, whose CV chunk buries the
// certificate under tool lists and puts him at dense rank 106. The cross-encoder does.
// Question 3 is not here: it needs a step-by-step table of its own, and lives in
// CompoundQuestion.vue.
const questions = [
  { n: 1, text: 'Welke AI tools mag ik gebruiken?',
    stages: [{ at: 0, verdict: 'ok', detail: '', fix: 'Naive' }] },
  { n: 2, text: 'Ik wil AZ-900 halen, wie heeft dat certificaat al?', stages: [
    { at: 1, verdict: 'no', detail: '1 / 4 holders', fix: 'Naive' },
    { at: 2, verdict: 'part', detail: '3 / 4 holders', fix: 'Hybrid search' },
    { at: 3, verdict: 'ok', detail: '4 / 4 holders', fix: 'Reranking' },
  ] },
  { n: 4, text: 'Hoeveel credits heeft Simon nog?',
    stages: [{ at: 0, verdict: 'no', detail: 'no chunk holds the sum', fix: 'Structure' }] },
]

const asked = computed(() =>
  props.show ? questions.filter(q => props.show.includes(q.n)) : questions
)
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
  padding: 0 1.1rem 0.6rem;
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
  padding: 0.75rem 1.1rem;
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
.stages {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.stage {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1.1rem;
}
.mark { flex: 0 0 var(--mark-col); display: flex; justify-content: center; }
.fix { flex: 0 0 var(--fix-col); text-align: center; }

.detail,
.row .fix {
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
.row .fix {
  background: #ffe2d2;
  color: #8a2f00;
}
/* Row 1 has nothing to fix, and an empty chip is still a coloured rectangle. */
.detail:empty,
.row .fix:empty {
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
.verdict.part {
  border-color: #b8791f;
  background: #fdf3e0;
  color: #8a5a10;
}
.verdict.no {
  border-color: #b23c2c;
  color: #b23c2c;
}
</style>
