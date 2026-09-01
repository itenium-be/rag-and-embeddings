<template>
  <div class="dotp">

    <div class="calc">
      <div class="crow reveal" :class="{ shown: clicks >= 1 }">
        <span class="vlabel">
          the question
          <em>Welke AI tools mag ik gebruiken?</em>
        </span>
        <span class="cells">
          <span v-for="(n, i) in question" :key="i" class="cell">{{ n }}</span>
          <span class="cell more">…</span>
        </span>
      </div>

      <div class="crow ops reveal" :class="{ shown: clicks >= 2 }">
        <span class="vlabel"></span>
        <span class="cells">
          <span v-for="i in 6" :key="i" class="op">×</span>
          <span class="op"></span>
        </span>
      </div>

      <div class="crow reveal" :class="{ shown: clicks >= 1 }">
        <span class="vlabel">
          the chunk
          <em>Approved AI Tools itenium</em>
        </span>
        <span class="cells">
          <span v-for="(n, i) in chunk" :key="i" class="cell">{{ n }}</span>
          <span class="cell more">…</span>
        </span>
      </div>

      <div class="crow ops reveal" :class="{ shown: clicks >= 3 }">
        <span class="vlabel"></span>
        <span class="cells">
          <span v-for="i in 6" :key="i" class="op down">&darr;</span>
          <span class="op"></span>
        </span>
      </div>

      <div class="crow reveal" :class="{ shown: clicks >= 3 }">
        <span class="vlabel"></span>
        <span class="cells">
          <span v-for="(n, i) in products" :key="i" class="cell product">{{ n }}</span>
          <span class="cell more">…</span>
        </span>
      </div>

      <div class="calcfoot">
        <span class="rest reveal" :class="{ shown: clicks >= 4 }">and 378 more</span>
        <span class="res reveal" :class="{ shown: clicks >= 4 }">= 0.887</span>
      </div>
    </div>

    <div class="cosline reveal" :class="{ shown: clicks >= 5 }">
      Every vector has length&nbsp;1, so the dot product <b>is</b> the cosine.
    </div>

    <div class="scale reveal" :class="{ shown: clicks >= 6 }">
      <div class="bar">
        <span class="band"></span>
        <span class="pin"></span>
        <span class="pinlabel">0.887</span>
      </div>
      <div class="ticks">
        <span class="tick" style="left: 0">0.0</span>
        <span class="tick edge" style="left: 67.2%">0.672</span>
        <span class="tick" style="left: 100%">1.0</span>
      </div>
      <div class="scap">
        all 404 549 chunk pairs — min <b>0.672</b> · median <b>0.800</b> · max <b>0.999</b>
      </div>
    </div>

    <div class="punch reveal" :class="{ shown: clicks >= 7 }">
      Never near zero. Nearness is a ranking, not a threshold.
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// The first six of the 384 real dimensions and their real products: question 1 of the
// scoreboard against the chunk naive retrieval actually returns for it. Three decimals
// on the inputs is what makes the products on screen reproduce by hand.
const question = ['+0.082', '−0.038', '−0.064', '−0.043', '+0.027', '−0.057']
const chunk = ['+0.026', '−0.038', '−0.039', '−0.084', '+0.028', '−0.026']
const products = ['+0.0022', '+0.0014', '+0.0025', '+0.0036', '+0.0008', '+0.0015']
</script>

<style scoped>
.dotp {
  display: flex;
  flex-direction: column;
  margin-top: 0.7rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.crow {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.3rem 0;
}
.crow.ops { padding: 0; }

.vlabel {
  flex: 0 0 15rem;
  display: flex;
  flex-direction: column;
  font-size: 1.05rem;
  color: #1c1c1c;
}
.vlabel em {
  font-style: normal;
  font-size: 0.82rem;
  line-height: 1.2;
  margin-top: 0.15rem;
  color: #5f6066;
}

/* One shared seven-column grid for values and operators alike, so every × and ↓ sits
   on the centre line of the pair it belongs to. */
.cells {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.4rem;
}
.cell {
  font-family: var(--font-code);
  font-size: 0.88rem;
  text-align: center;
  border: 2px solid #a8a8a8;
  border-radius: 0.35rem;
  background: #fefefe;
  padding: 0.28rem 0;
  color: #33343a;
}
.cell.product {
  font-size: 0.8rem;
  border-color: var(--color-primary);
  color: #8a2f00;
  background: #ffe2d2;
}
.cell.more {
  border-color: transparent;
  background: transparent;
  color: #5f6066;
}

.op {
  font-family: var(--font-code);
  font-size: 0.95rem;
  line-height: 1.3;
  text-align: center;
  color: var(--color-primary);
}
.op.down { font-size: 1.05rem; }

.calcfoot {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 1.2rem;
  padding-top: 0.5rem;
}
.rest {
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.03em;
  color: #5f6066;
}
.res {
  font-family: var(--font-code);
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-primary);
}

.cosline {
  font-size: 1.05rem;
  padding-top: 1rem;
  color: #33343a;
}

.scale { padding-top: 1.5rem; }
.bar {
  position: relative;
  height: 2.1rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
}
/* The corpus occupies the right third and nothing else: the empty left two thirds is
   the whole point of the slide, so the band is drawn, not described. */
.band {
  position: absolute;
  left: 67.2%;
  right: 0.1%;
  top: 0;
  bottom: 0;
  background: #edf6ee;
  border-left: 2px solid #3f8a46;
  border-right: 2px solid #3f8a46;
}
.pin {
  position: absolute;
  left: 88.7%;
  top: -0.4rem;
  bottom: -0.4rem;
  width: 3px;
  background: var(--color-primary);
}
.pinlabel {
  position: absolute;
  left: 88.7%;
  bottom: 100%;
  transform: translateX(-50%);
  margin-bottom: 0.5rem;
  font-family: var(--font-code);
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
  color: var(--color-primary);
}

.ticks {
  position: relative;
  height: 1.1rem;
  margin-top: 0.35rem;
}
.tick {
  position: absolute;
  transform: translateX(-50%);
  font-family: var(--font-code);
  font-size: 0.8rem;
  color: #5f6066;
}
.tick.edge { color: #276b2e; }

.scap {
  font-size: 0.9rem;
  margin-top: 0.25rem;
  color: #5f6066;
}
.scap b {
  font-family: var(--font-code);
  font-weight: 700;
  color: #33343a;
}

.punch {
  font-size: 1.2rem;
  font-weight: 700;
  padding-top: 1.4rem;
  color: #1c1c1c;
}
</style>
