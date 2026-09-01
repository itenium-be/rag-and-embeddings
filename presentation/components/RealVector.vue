<template>
  <div class="real-vector">

    <div class="source reveal" :class="{ shown: clicks >= 1 }">
      <div class="source-file">Itenium - CV Bert Vermorgen - ENG.docx</div>
      <div class="source-text">Bert Vermorgen .NET Developer (7 years of experience)</div>
    </div>

    <div class="riser reveal" :class="{ shown: clicks >= 2 }">
      <span class="arrow">&darr;</span>
      <span class="model">intfloat/multilingual-e5-small</span>
    </div>

    <div class="grid reveal" :class="{ shown: clicks >= 2 }">
      <span v-for="(v, i) in values" :key="i" class="n">{{ v }}</span>
      <span class="more">&hellip;</span>
    </div>

    <div class="count reveal" :class="{ shown: clicks >= 3 }">
      <span class="tokens">384 numbers / dims</span>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// The real embedding of that CV line, straight out of the demo index — the first 48
// of its 384 dimensions. Regenerate from app/data/index-real if the model changes.
const values = [
  '+0.038', '+0.034', '-0.038', '-0.013', '+0.046', '-0.036', '-0.009', '+0.005',
  '+0.015', '+0.023', '+0.029', '+0.010', '+0.064', '-0.069', '-0.026', '+0.055',
  '+0.073', '-0.069', '-0.129', '-0.054', '+0.035', '-0.003', '-0.020', '+0.037',
  '+0.042', '+0.076', '-0.019', '-0.022', '+0.074', '-0.087', '-0.072', '-0.029',
  '+0.069', '-0.041', '+0.056', '+0.003', '-0.086', '-0.023', '+0.069', '-0.065',
  '-0.033', '+0.020', '+0.028', '+0.081', '+0.021', '+0.023', '+0.009', '+0.038',
]
</script>

<style scoped>
.real-vector {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 1.4rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.source {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  background: #fefefe;
  padding: 0.5rem 1.4rem 0.7rem;
  text-align: center;
}
.source-file {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.03em;
  color: #5f6066;
}
.source-text {
  font-size: 1.3rem;
  margin-top: 0.2rem;
  color: #1c1c1c;
}

.riser {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.7rem 0;
}
.arrow {
  font-size: 1.6rem;
  line-height: 1;
  color: var(--color-primary);
}
.model {
  font-family: var(--font-code);
  font-size: 0.95rem;
  color: #5f6066;
}

/* Eight to a row on purpose: rows and columns read as coordinates, where the same
   numbers set as a paragraph would read as noise. */
.grid {
  display: grid;
  grid-template-columns: repeat(8, auto);
  gap: 0.55rem 1.1rem;
  justify-items: end;
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  background: #fefefe;
  padding: 1.1rem 1.8rem 1.2rem;
}
.n {
  font-family: var(--font-code);
  font-size: 1.25rem;
  line-height: 1.1;
  color: #33343a;
}
.more {
  grid-column: 1 / -1;
  justify-self: center;
  font-family: var(--font-code);
  font-size: 1.25rem;
  line-height: 1;
  padding-top: 0.2rem;
  color: #5f6066;
}

.count { padding-top: 1.1rem; }
.tokens {
  font-family: var(--font-code);
  font-size: 1.05rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem 0.3rem;
  border-radius: 0.35rem;
  background: #343434;
  color: #fefefe;
}
</style>
