<template>
  <div class="with-rag">
    <div class="flow">

      <div class="row" :class="{ lit: clicks >= 1 }">
        <div class="actor">
          <ProgrammerGlyph />
          <div class="actor-label">you</div>
        </div>
        <span class="arrow">&rarr;</span>
        <div class="prompt">
          <div class="tag">Prompt</div>
          <div class="prompt-text">when does the bakery close?</div>
        </div>
      </div>

      <div class="riser" :class="{ lit: clicks >= 2 }">&darr;</div>

      <div class="ragbox" :class="{ lit: clicks >= 2 }">
        <div class="rag-tag">RAG</div>
        <div class="rag-inner">
          <div class="step" :class="{ lit: clicks >= 2 }">
            <div class="step-name"><span class="step-letter">R</span>ETRIEVAL</div>
            <div class="step-body">query an authoritative source</div>
          </div>
          <span class="step-arrow" :class="{ lit: clicks >= 3 }">&rarr;</span>
          <div class="step" :class="{ lit: clicks >= 3 }">
            <div class="step-name"><span class="step-letter">A</span>UGMENTED</div>
            <div class="step-body">show the full prompt</div>
          </div>
        </div>
      </div>

      <div class="riser" :class="{ lit: clicks >= 4 }">&darr;</div>

      <div class="row" :class="{ lit: clicks >= 4 }">
        <div class="actor">
          <StochasticParrot />
          <div class="actor-label"><span class="step-letter">G</span>ENERATION</div>
        </div>
        <span class="arrow" :class="{ lit: clicks >= 5 }">&rarr;</span>
        <div class="answer" :class="{ lit: clicks >= 5 }">
          <div class="tag good">Correct answer</div>
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
  align-items: center;
  margin: 0.2rem -2.5rem 0 -6rem;
}

.row,
.riser,
.ragbox,
.step,
.step-arrow,
.answer,
.arrow {
  opacity: 0.28;
  transition: opacity 350ms ease, border-color 350ms ease, box-shadow 350ms ease;
}
.lit { opacity: 1; }

.row {
  display: flex;
  align-items: center;
  gap: 1.1rem;
}

.actor { flex: 0 0 9rem; text-align: center; }
.actor :deep(svg) { width: 4.6rem; height: auto; margin: 0 auto 0.15rem; }
.actor-label {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #232323;
}

.arrow {
  font-size: 1.9rem;
  line-height: 1;
  color: var(--color-primary);
}

.riser {
  font-size: 1.7rem;
  line-height: 1;
  margin: 0.15rem 0;
  color: var(--color-primary);
}

.tag {
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.06em;
  color: #7a7b80;
}
.tag.good { color: #2f6d35; }

.prompt,
.answer {
  border: 2px solid #c4c4c4;
  border-radius: 0.6rem;
  padding: 0.6rem 1.2rem 0.7rem;
  background: #fefefe;
  text-align: left;
}
.prompt-text {
  font-family: var(--font-code);
  font-size: 1.15rem;
  margin-top: 0.25rem;
  color: #232323;
}
.answer.lit {
  border-color: #4f9a55;
  background: #eff7f0;
}
.answer-text {
  font-size: 1.15rem;
  margin-top: 0.25rem;
  color: #232323;
}

.ragbox {
  border: 2px solid #343434;
  border-radius: 0.8rem;
  background: #343434;
  padding: 0.7rem 1.1rem 1.1rem;
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
  color: #c9c9c9;
  text-align: left;
  margin-bottom: 0.55rem;
}

.rag-inner {
  display: flex;
  align-items: center;
  gap: 0.9rem;
}

.step {
  flex: 0 0 16rem;
  border-radius: 0.55rem;
  background: #fefefe;
  padding: 0.6rem 0.9rem 0.7rem;
  text-align: center;
}
.step-arrow {
  font-size: 1.6rem;
  line-height: 1;
  color: var(--color-primary);
}
.step-name {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #232323;
}
.step-letter { color: var(--color-primary); }
.step-body {
  font-size: 0.92rem;
  line-height: 1.4;
  margin-top: 0.35rem;
  color: #4a4b50;
}
</style>
