<template>
  <div class="dotp">

    <div class="calc">
      <div v-for="v in vectors" :key="v.what" class="vrow reveal" :class="{ shown: clicks >= 1 }">
        <span class="vlabel">
          {{ v.what }}
          <em>{{ v.text }}</em>
        </span>
        <span class="cells">
          <span v-for="(n, i) in v.dims" :key="i" class="cell">{{ n }}</span>
          <span class="cell more">…</span>
        </span>
      </div>

      <div class="calcfoot">
        <span class="op reveal" :class="{ shown: clicks >= 1 }">multiply pairwise, add all 384</span>
        <span class="res reveal" :class="{ shown: clicks >= 2 }">= 0.887</span>
      </div>
    </div>

    <div class="cosline reveal" :class="{ shown: clicks >= 2 }">
      Every vector has length&nbsp;1, so the dot product <b>is</b> the cosine.
    </div>

    <div class="scale reveal" :class="{ shown: clicks >= 3 }">
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

    <div class="punch reveal" :class="{ shown: clicks >= 4 }">
      Never near zero. Nearness is a ranking, not a threshold.
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// The first six of the 384 real dimensions, and the real cosine between them: question 1
// of the scoreboard against the chunk naive retrieval actually returns for it.
const vectors = [
  {
    what: 'the question',
    text: 'Welke AI tools mag ik gebruiken?',
    dims: ['+0.08', '−0.04', '−0.06', '−0.04', '+0.03', '−0.06'],
  },
  {
    what: 'the chunk',
    text: 'Approved AI Tools itenium',
    dims: ['+0.03', '−0.04', '−0.04', '−0.08', '+0.03', '−0.03'],
  },
]
</script>

<style scoped>
.dotp {
  display: flex;
  flex-direction: column;
  margin-top: 1rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.vrow {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 0;
}
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

.cells {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.4rem;
}
.cell {
  font-family: var(--font-code);
  font-size: 0.95rem;
  text-align: center;
  border: 2px solid #a8a8a8;
  border-radius: 0.35rem;
  background: #fefefe;
  padding: 0.3rem 0;
  color: #33343a;
}
.cell.more {
  border-color: transparent;
  background: transparent;
  color: #5f6066;
}

.calcfoot {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  gap: 1.2rem;
  padding-top: 0.5rem;
}
.op {
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
  padding-top: 1.3rem;
  color: #33343a;
}

.scale { padding-top: 2.2rem; }
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
  margin-bottom: 0.55rem;
  font-family: var(--font-code);
  font-size: 0.9rem;
  font-weight: 700;
  white-space: nowrap;
  color: var(--color-primary);
}

.ticks {
  position: relative;
  height: 1.2rem;
  margin-top: 0.4rem;
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
  margin-top: 0.3rem;
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
  padding-top: 2.2rem;
  color: #1c1c1c;
}
</style>
