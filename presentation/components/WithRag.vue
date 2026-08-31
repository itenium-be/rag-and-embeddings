<template>
  <div class="with-rag">
    <div class="flow">

      <div class="band top" :class="{ lit: clicks >= 1 }">
        <div class="prompt col-retrieval">
          <div class="tag">Prompt</div>
          <div class="prompt-text">when does the bakery close?</div>
        </div>
        <span class="arrow">&larr;</span>
        <div class="actor">
          <ProgrammerGlyph />
          <div class="actor-label">you</div>
        </div>
      </div>

      <div class="band">
        <div class="col-retrieval riser" :class="{ lit: clicks >= 2 }">&darr;</div>
      </div>

      <div class="ragbox" :class="{ lit: clicks >= 2 }">
        <div class="rag-tag">RAG</div>
        <div class="rag-inner">
          <div class="step col-retrieval" :class="{ lit: clicks >= 2 }">
            <div class="step-name"><span class="step-letter">R</span>ETRIEVAL</div>
            <div class="step-body">query an authoritative source</div>
          </div>
          <span class="step-arrow" :class="{ lit: clicks >= 3 }">&rarr;</span>
          <div class="step col-augmented" :class="{ lit: clicks >= 3 }">
            <div class="step-name"><span class="step-letter">A</span>UGMENTED</div>
            <pre class="step-prompt"><span class="ctx">Bakery De Korenbloem
Mon-Sat  07:00-18:30
Sun + holidays: closed</span>

when does the bakery close?</pre>
          </div>
        </div>
      </div>

      <div class="band right">
        <div class="col-augmented riser" :class="{ lit: clicks >= 4 }">&darr;</div>
      </div>

      <div class="band right" :class="{ lit: clicks >= 4 }">
        <div class="answer" :class="{ lit: clicks >= 5 }">
          <div class="tag good">Correct answer</div>
          <div class="answer-text">closed today, it&rsquo;s a holiday</div>
        </div>
        <span class="arrow" :class="{ lit: clicks >= 5 }">&larr;</span>
        <div class="col-augmented actor-slot">
          <div class="actor">
            <StochasticParrot />
            <div class="actor-label"><span class="step-letter">G</span>ENERATION</div>
          </div>
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
  margin: 0.2rem -2.5rem 0 -6rem;
  text-align: initial;
}

/* Column widths are shared by every row, so the risers drop straight from the
   Prompt into RETRIEVAL and out of AUGMENTED into GENERATION. */
.col-retrieval { flex: 0 0 15rem; }
.col-augmented { flex: 0 0 24rem; }

/* Matches .ragbox's border + padding so a band's columns sit exactly above the
   box's inner columns. */
.band {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 calc(1.1rem + 2px);
}
.band.right { justify-content: flex-end; }

.actor-slot { display: flex; justify-content: center; }

.band,
.riser,
.ragbox,
.step,
.step-arrow,
.answer,
.arrow {
  opacity: 0.55;
  transition: opacity 350ms ease, border-color 350ms ease, box-shadow 350ms ease;
}
.lit { opacity: 1; }

.actor { flex: 0 0 8rem; text-align: center; }
.actor :deep(svg) { width: 4rem; height: auto; margin: 0 auto 0.1rem; }
.actor-label {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #1c1c1c;
}

.arrow {
  font-size: 1.9rem;
  line-height: 1;
  color: var(--color-primary);
}

.riser {
  font-size: 1.5rem;
  line-height: 1;
  margin: 0;
  text-align: center;
  color: var(--color-primary);
}

.tag {
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.06em;
  color: #5f6066;
}
.tag.good { color: #276b2e; }

.prompt,
.answer {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  padding: 0.5rem 1.1rem 0.55rem;
  background: #fefefe;
  box-sizing: border-box;
}
.prompt-text,
.answer-text {
  font-size: 1.05rem;
  margin-top: 0.2rem;
  color: #1c1c1c;
}
.prompt-text { font-family: var(--font-code); }
.answer {
  flex: 0 0 auto;
}
.answer.lit {
  border-color: #3f8a46;
  background: #edf6ee;
}

.ragbox {
  border: 2px solid #343434;
  border-radius: 0.8rem;
  background: #343434;
  padding: 0.5rem 1.1rem 0.7rem;
}
.ragbox.lit {
  border-color: var(--color-primary);
  box-shadow: 0 10px 26px rgba(232, 71, 0, 0.2);
}
.rag-tag {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: 0.16em;
  color: #dcdcdc;
  margin-bottom: 0.35rem;
}

/* space-between, so AUGMENTED's right edge reaches the box's content edge and
   the riser below it lines up. */
.rag-inner {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 1rem;
}

.step {
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 0.55rem;
  background: #fefefe;
  padding: 0.6rem 0.9rem 0.7rem;
  box-sizing: border-box;
}
.step-arrow {
  align-self: center;
  font-size: 1.6rem;
  line-height: 1;
  color: var(--color-primary);
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
  margin-top: 0.35rem;
  color: #33343a;
  text-align: center;
}

.step-prompt {
  font-family: var(--font-code);
  font-size: 0.74rem;
  line-height: 1.35;
  margin: 0.35rem 0 0;
  color: #1c1c1c;
  white-space: pre;
}
.ctx {
  background: #ffe2d2;
  box-shadow: 0 0 0 2px #ffe2d2;
  border-radius: 2px;
  color: #8a2f00;
}
</style>
