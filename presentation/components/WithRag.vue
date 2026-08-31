<template>
  <div class="with-rag">
    <div class="chain">

      <div class="node actor" :class="{ lit: clicks >= 1 }">
        <ProgrammerGlyph />
        <div class="node-label">you</div>
      </div>

      <div class="arrow" :class="{ lit: clicks >= 2 }">&rarr;</div>

      <div class="node card" :class="{ lit: clicks >= 2 }">
        <div class="card-title">Prompt</div>
        <div class="card-body mono">when does the bakery close?</div>
      </div>

      <div class="arrow" :class="{ lit: clicks >= 3 }">&rarr;</div>

      <div class="node ragbox" :class="{ lit: clicks >= 3 }">
        <div class="rag-name">RAG</div>
        <div class="rag-sub">add context</div>
      </div>

      <div class="arrow" :class="{ lit: clicks >= 4 }">&rarr;</div>

      <div class="node actor" :class="{ lit: clicks >= 4 }">
        <StochasticParrot />
        <div class="node-label">LLM</div>
      </div>

      <div class="arrow" :class="{ lit: clicks >= 5 }">&rarr;</div>

      <div class="node card answer" :class="{ lit: clicks >= 5 }">
        <div class="card-title">Correct answer</div>
        <div class="card-body">closed today, it&rsquo;s a holiday</div>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.with-rag { text-align: center; }

.chain {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 2.4rem -2.5rem 0 -6rem;
}

.node,
.arrow {
  opacity: 0.2;
  filter: grayscale(1);
  transition: opacity 400ms ease, filter 400ms ease, border-color 400ms ease, box-shadow 400ms ease;
}
.node.lit,
.arrow.lit {
  opacity: 1;
  filter: none;
}

.arrow {
  flex: 0 0 auto;
  font-size: 1.9rem;
  line-height: 1;
  color: var(--color-primary);
}

.actor { flex: 0 0 8rem; text-align: center; }
.actor :deep(svg) { width: 6.4rem; height: auto; margin: 0 auto 0.3rem; }
.node-label {
  font-family: var(--font-code);
  font-size: 1.05rem;
  font-weight: 500;
  color: #232323;
}

.card {
  flex: 0 0 9.6rem;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 9.5rem;
  box-sizing: border-box;
  border: 2px solid #d8d8d8;
  border-radius: 0.6rem;
  padding: 0.9rem 0.8rem;
  background: #fefefe;
  text-align: center;
}
.card.lit { border-color: var(--color-primary); }
.card.answer.lit {
  border-color: #4f9a55;
  background: #f2f8f2;
}

.card-title {
  font-family: var(--font-heading);
  font-size: 1rem;
  font-weight: 500;
  color: #232323;
}
.card.answer.lit .card-title { color: #2f6d35; }

.card-body {
  font-size: 0.85rem;
  line-height: 1.45;
  margin-top: 0.5rem;
  color: #5b5c62;
}
.card-body.mono { font-family: var(--font-code); }

.ragbox {
  flex: 0 0 9.6rem;
  align-self: stretch;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 9.5rem;
  box-sizing: border-box;
  border: 2px solid #343434;
  border-radius: 0.7rem;
  background: #343434;
  padding: 0.9rem 0.8rem;
  text-align: center;
}
.ragbox.lit {
  border-color: var(--color-primary);
  box-shadow: 0 8px 20px rgba(232, 71, 0, 0.18);
}

.rag-name {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 2.2rem;
  line-height: 1;
  letter-spacing: 0.06em;
  color: var(--color-primary-muted);
}
.ragbox.lit .rag-name { color: var(--color-primary); }

.rag-sub {
  font-family: var(--font-code);
  font-size: 0.85rem;
  margin-top: 0.5rem;
  color: #c9c9c9;
}
</style>
