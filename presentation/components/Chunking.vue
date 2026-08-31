<template>
  <div class="chunking">

    <div class="row">

      <div class="side reveal" :class="{ shown: clicks >= 1 }">
        <div class="doc">
          <span v-for="n in 9" :key="n" class="rule" :class="{ short: n % 4 === 0 }"></span>
        </div>
        <div class="name">Arbeidsreglement.pdf</div>
        <div class="count">37 pages</div>
      </div>

      <span class="arrow reveal" :class="{ shown: clicks >= 2 }">&rarr;</span>

      <div class="side reveal" :class="{ shown: clicks >= 2 }">
        <div class="deck">
          <span v-for="n in 5" :key="n" class="card" :style="cardStyle(n)"></span>
        </div>
        <div class="name">index cards</div>
        <div class="count">133 chunks</div>
      </div>

    </div>

    <div class="zoom reveal" :class="{ shown: clicks >= 3 }">
      <div class="zoom-loc">Arbeidsreglement &gt; p. 5</div>
      <div class="zoom-text"><span
        class="torn reveal" :class="{ shown: clicks >= 4 }"
      >de bedienden</span> wordt per maand berekend en uiterlijk de laatste
        kalenderdag van de maand betaald. De uitbetaling gebeurt door middel van
        een bankoverschrijving.</div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Fanned by hand. Five cards is enough to read as a stack without the angles
// turning into a mess.
const angles = [-7, -3.5, 0, 3.5, 7]
const cardStyle = (n) => ({
  transform: `rotate(${angles[n - 1]}deg) translateY(${Math.abs(angles[n - 1]) * 0.35}px)`,
  zIndex: String(n === 3 ? 5 : 3 - Math.abs(n - 3)),
})
</script>

<style scoped>
.chunking {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 0.8rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.row {
  display: flex;
  align-items: center;
  gap: 2.6rem;
}
.side {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 17rem;
}

.doc {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.55rem;
  width: 8.2rem;
  height: 11rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
  padding: 0 1rem;
}
.rule {
  height: 0.35rem;
  border-radius: 0.2rem;
  background: #d5d5d5;
}
.rule.short { width: 55%; }

.deck {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 11rem;
}
.card {
  position: absolute;
  width: 7rem;
  height: 4.6rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.07);
}

.name {
  font-size: 1.1rem;
  margin-top: 0.9rem;
  color: #1c1c1c;
}
.count {
  font-family: var(--font-code);
  font-size: 0.95rem;
  font-weight: 600;
  margin-top: 0.45rem;
  padding: 0.2rem 0.6rem 0.25rem;
  border-radius: 0.35rem;
  background: #343434;
  color: #fefefe;
}

.arrow {
  font-size: 2rem;
  line-height: 1;
  color: var(--color-primary);
}

.zoom {
  width: 44rem;
  margin-top: 1.6rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.7rem 1.2rem 0.9rem;
}
.zoom-loc {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.03em;
  color: #5f6066;
}
.zoom-text {
  font-size: 1.1rem;
  line-height: 1.45;
  margin-top: 0.3rem;
  color: #33343a;
}
/* The card really does start here, mid-sentence: what it was about stayed on the
   card before it. */
.torn {
  background: #ffe2d2;
  box-shadow: 0 0 0 2px #ffe2d2;
  border-radius: 2px;
  color: #8a2f00;
}
</style>
