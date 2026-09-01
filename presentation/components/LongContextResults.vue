<template>
  <div class="longcontext">

    <div class="head">
      <span class="head-label mark">context</span>
      <span class="head-label fix">RAG fixes it at</span>
    </div>

    <div v-for="q in questions" :key="q.text" class="row">
      <span class="q">{{ q.text }}</span>
      <span class="detail">{{ q.detail }}</span>
      <span class="mark">
        <span class="verdict" :class="q.verdict">{{ MARK[q.verdict] }}</span>
      </span>
      <span class="fix">{{ q.fix }}</span>
    </div>

    <div class="callouts">
      <div class="callout reveal" :class="{ shown: clicks >= 1 }">
        <div class="kicker">IT ARGUES WITH ITSELF</div>
        <p class="quote">"De bronnen bevatten geen enkele vermelding van een AZ-900-certificaat."</p>
        <p class="quote">&hellip; lists all four holders &hellip;</p>
        <p class="quote">"Correctie: die zijn w&eacute;l AZ-900."</p>
      </div>

      <div class="callout reveal" :class="{ shown: clicks >= 2 }">
        <div class="kicker">IT WILL NOT ADD UP</div>
        <p class="quote">"Optellen van alle boekingen op zijn naam levert een getal op,
          maar de bronnen zeggen niet dat dat het actuele saldo is."</p>
        <p class="aside">All 946 ledger rows were in the prompt.</p>
      </div>
    </div>

    <div class="money reveal" :class="{ shown: clicks >= 3 }">
      <span class="side">
        <b>501k tokens</b>
        <span class="cost">$4.93</span>
        <span class="what">everything, every question</span>
      </span>
      <span class="versus">vs</span>
      <span class="side rag">
        <b>500 tokens</b>
        <span class="cost">$0.0025</span>
        <span class="what">5 retrieved chunks</span>
      </span>
    </div>

  </div>
</template>

<script setup>
defineProps({
  clicks: { type: Number, default: 0 },
})

const MARK = { ok: '✓', part: '!', no: '✗' }

// Measured, not predicted: every verdict is one `app/questions.yaml` holds under the
// `-1` key and `tests/test_scoreboard.py` asserts against data/index-real. `detail` is
// the answer critic's tally, because at this step there is nothing retrieved to count -
// the whole corpus is in the prompt by construction.
const questions = [
  { text: 'Welke AI tools mag ik gebruiken?', detail: '5 / 5 facts', verdict: 'ok', fix: 'Naive' },
  { text: 'Kan ik een fiets leasen?', detail: '2 / 2 facts', verdict: 'ok', fix: 'Naive' },
  { text: 'Wie heeft AZ-900 al?', detail: '6 / 6 facts', verdict: 'ok', fix: 'Reranking' },
  { text: 'Laptoplader kwijt, wat nu?', detail: '4 / 5 facts', verdict: 'part', fix: 'Query rewriting' },
  { text: 'Hoeveel credits heeft Simon nog?', detail: '0 / 1 facts', verdict: 'no', fix: 'Structure' },
]
</script>

<style scoped>
.longcontext {
  --mark-col: 4.5rem;
  --fix-col: 10.5rem;
  margin-top: 0.6rem;
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
  padding: 0 1.1rem 0.5rem;
}
.head-label {
  font-family: var(--font-code);
  font-size: 0.8rem;
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
  padding: 0.5rem 1.1rem;
  margin-bottom: 0.5rem;
}
.q {
  flex: 1;
  font-size: 1.05rem;
  color: #33343a;
}

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
.mark { flex: 0 0 var(--mark-col); display: flex; justify-content: center; }
.fix {
  flex: 0 0 var(--fix-col);
  text-align: center;
  background: #ffe2d2;
  color: #8a2f00;
}

.verdict {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.8rem;
  height: 1.8rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.35rem;
  font-size: 1.1rem;
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

.callouts {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}
.callout {
  flex: 1;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fbfbfb;
  padding: 0.6rem 0.9rem 0.7rem;
}
.kicker {
  font-family: var(--font-code);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  color: #b23c2c;
  margin-bottom: 0.35rem;
}
.quote {
  margin: 0 0 0.2rem;
  font-size: 0.82rem;
  line-height: 1.35;
  color: #33343a;
}
.aside {
  margin: 0.3rem 0 0;
  font-family: var(--font-code);
  font-size: 0.72rem;
  color: #5f6066;
}

.money {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  margin-top: 1rem;
}
.side {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}
.side b {
  font-family: var(--font-code);
  font-size: 1.3rem;
  color: #33343a;
}
.cost {
  font-family: var(--font-code);
  font-size: 1.3rem;
  font-weight: 600;
  color: #b23c2c;
}
.side.rag .cost { color: #276b2e; }
.what {
  font-size: 0.78rem;
  color: #5f6066;
}
.versus {
  font-family: var(--font-code);
  font-size: 0.85rem;
  color: #5f6066;
}
</style>
