<template>
  <div class="with-rag">
    <div class="flow">

      <div class="band">
        <div class="col-retrieval prompt reveal" :class="{ shown: clicks >= 1 }">
          <div class="tag">Prompt</div>
          <div class="prompt-text">when does the bakery close?</div>
        </div>
        <span class="arrow reveal" :class="{ shown: clicks >= 1 }">&larr;</span>
        <div class="actor reveal" :class="{ shown: clicks >= 1 }">
          <ProgrammerGlyph />
          <div class="actor-label">you</div>
        </div>
      </div>

      <div class="band">
        <div class="col-retrieval riser reveal" :class="{ shown: clicks >= 2 }">&darr;</div>
      </div>

      <div class="ragbox">
        <div class="grid">
          <div class="cell top-left">
            <div class="step reveal" :class="{ shown: clicks >= 2 }">
              <div class="step-name"><span class="step-letter">R</span>ETRIEVAL</div>
              <div class="step-body">query an authoritative source</div>
            </div>
          </div>

          <div class="cell mid">
            <span class="arrow reveal" :class="{ shown: clicks >= 3 }">&rarr;</span>
          </div>

          <div class="cell top-right">
            <div class="step reveal" :class="{ shown: clicks >= 3 }">
              <div class="step-name"><span class="step-letter">A</span>UGMENTED</div>
              <pre class="step-prompt"><span class="ctx">Bakery De Korenbloem
Mon-Sat  07:00-18:30
Sun + holidays: closed</span>

when does the bakery close?</pre>
            </div>
          </div>

          <div class="cell drop">
            <span class="riser reveal" :class="{ shown: clicks >= 4 }">&darr;</span>
          </div>

          <div class="cell bottom-right">
            <div class="gen reveal" :class="{ shown: clicks >= 4 }">
              <div class="gen-label"><span class="step-letter">G</span>ENERATION</div>
              <StochasticParrot />
            </div>
          </div>
        </div>
      </div>

      <div class="band right">
        <div class="col-augmented riser reveal" :class="{ shown: clicks >= 5 }">&darr;</div>
      </div>

      <div class="band right">
        <div class="answer reveal" :class="{ shown: clicks >= 5 }">
          <div class="tag good">Answer</div>
          <div class="answer-text">closed today, it&rsquo;s a holiday</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.with-rag { text-align: center; }

.flow {
  display: inline-flex;
  flex-direction: column;
  margin: 0 -2.5rem 0 -6rem;
  text-align: initial;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.col-retrieval { flex: 0 0 19rem; }
.col-augmented { flex: 0 0 24rem; }

/* Matches .ragbox's border + padding so the risers line up with its columns. */
.band {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 calc(0.9rem + 2px);
}
.band.right { justify-content: flex-end; }

.actor { flex: 0 0 7rem; text-align: center; }
.actor :deep(svg) { width: 3.2rem; height: auto; margin: 0 auto 0.1rem; }
.actor-label {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #1c1c1c;
}

.arrow {
  font-size: 1.7rem;
  line-height: 1;
  color: var(--color-primary);
}

.riser {
  display: block;
  font-size: 1.2rem;
  line-height: 1.1;
  text-align: center;
  color: var(--color-primary);
}

.tag {
  font-family: var(--font-code);
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  color: #5f6066;
}
.tag.good { color: #276b2e; }

.prompt,
.answer {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  padding: 0.3rem 1rem 0.4rem;
  background: #fefefe;
  box-sizing: border-box;
}
.prompt-text,
.answer-text {
  font-size: 1rem;
  margin-top: 0.15rem;
  color: #1c1c1c;
  white-space: nowrap;
}
.prompt-text { font-family: var(--font-code); }
.answer { flex: 0 0 auto; }
.answer.shown {
  border-color: #3f8a46;
  background: #edf6ee;
}

.ragbox {
  border: 2px solid var(--color-primary);
  border-radius: 0.8rem;
  background: #343434;
  padding: 0.45rem 0.9rem 0.55rem;
  box-shadow: 0 10px 26px rgba(232, 71, 0, 0.18);
}

/* X X
     X   — bottom-left stays empty on purpose. */
.grid {
  display: grid;
  grid-template-columns: 19rem auto 24rem;
  align-items: start;
}
.top-left    { grid-column: 1; grid-row: 1; }
.mid         { grid-column: 2; grid-row: 1; align-self: center; text-align: center; padding: 0 0.5rem; }
.top-right   { grid-column: 3; grid-row: 1; }
.drop        { grid-column: 3; grid-row: 2; text-align: center; }
.bottom-right{ grid-column: 3; grid-row: 3; }

.step {
  border-radius: 0.55rem;
  background: #fefefe;
  padding: 0.55rem 0.9rem 0.65rem;
  box-sizing: border-box;
}
.step-name {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #1c1c1c;
  text-align: center;
}
.step-letter { color: var(--color-primary); }
.step-body {
  font-size: 0.95rem;
  line-height: 1.4;
  margin-top: 0.3rem;
  color: #33343a;
  text-align: center;
}

.step-prompt {
  font-family: var(--font-code);
  font-size: 0.68rem;
  line-height: 1.25;
  margin: 0.3rem 0 0;
  color: #1c1c1c;
  white-space: pre;
}
.ctx {
  background: #ffe2d2;
  box-shadow: 0 0 0 2px #ffe2d2;
  border-radius: 2px;
  color: #8a2f00;
}

.gen { text-align: center; }
.gen-label {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #fefefe;
}
.gen :deep(svg) { width: 2.8rem; height: auto; margin: 0.15rem auto 0; }
</style>
