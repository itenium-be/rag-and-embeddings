<template>
  <div class="dotp">

    <div class="calc">
      <div class="crow reveal" :class="{ shown: clicks >= 1 }">
        <span class="vlabel">
          the question
          <em>Welke AI tools mag ik gebruiken?</em>
        </span>
        <span class="cells">
          <span
            v-for="(n, i) in questionCells" :key="i"
            class="cell" :class="{ swapped: isSwapped(i) }"
          >{{ n }}</span>
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
          <span
            v-for="(n, i) in chunkCells" :key="i"
            class="cell" :class="{ swapped: isSwapped(i) }"
          >{{ n }}</span>
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
          <span
            v-for="(n, i) in productCells" :key="i"
            class="cell product" :class="{ swapped: isSwapped(i) }"
          >
            <i
              v-if="i > 0"
              class="sign reveal" :class="{ shown: clicks >= 4, minus: isSwapped(i) }"
            >{{ isSwapped(i) ? '−' : '+' }}</i>
            {{ n }}
          </span>
          <span class="cell more">
            <i class="sign reveal" :class="{ shown: clicks >= 4 }">+</i>
            …
          </span>
        </span>
      </div>

      <div class="calcfoot">
        <span class="foot reveal" :class="{ shown: clicks === 4 || clicks >= 6 }">
          <span class="rest">and 378 more</span>
          <span class="res">= 0.887</span>
        </span>
        <span class="foot verdict reveal" :class="{ shown: clicks === 5 }">
          A big difference reduces the resulting score
        </span>
      </div>
    </div>

    <div class="scale reveal" :class="{ shown: clicks >= 6 }">
      <div class="stitle">our corpus</div>
      <div class="scount">every pair of the 2194 chunks — 2 405 721 comparisons</div>
      <div class="bar">
        <span class="band" :style="{ left: at(V.min), right: to(V.max) }"></span>
        <span
          class="box reveal" :class="{ shown: zoomed }"
          :style="{ left: at(V.p1), right: to(V.p99) }"
        ></span>
        <span
          class="medline reveal" :class="{ shown: zoomed }"
          :style="{ left: at(V.median) }"
        ></span>
        <span class="mark" :style="{ left: at(V.avg) }"></span>
        <span class="pin" :style="{ left: at(V.match) }"></span>
        <span class="avglabel" :class="{ wide: zoomed }" :style="{ left: at(V.avg) }">avg 0.812</span>
        <span class="pinlabel" :style="{ left: at(V.match) }">0.887</span>
      </div>
      <div class="ticks">
        <span class="tick min" :style="{ left: at(V.min) }">0.661</span>
        <span
          class="tick reveal" :class="{ shown: zoomed }" :style="{ left: at(V.p1) }"
        >p1 0.730</span>
        <span
          class="tick reveal" :class="{ shown: zoomed }" :style="{ left: at(V.median) }"
        >median 0.800</span>
        <span
          class="tick reveal" :class="{ shown: zoomed }" :style="{ left: at(V.p99) }"
        >p99 0.929</span>
        <span class="tick max" :style="{ left: at(V.max) }">0.999</span>
      </div>
    </div>


  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ clicks: { type: Number, default: 0 } })

// The first six of the 384 real dimensions and their real products: question 1 of the
// scoreboard against the chunk naive retrieval actually returns for it. Three decimals
// on the inputs is what makes the products on screen reproduce by hand. The sign lives
// in the operator between the boxes, so the boxes hold magnitudes only.
const question = ['+0.082', '−0.038', '−0.064', '−0.043', '+0.027', '−0.057']
const chunk = ['+0.026', '−0.038', '−0.039', '−0.084', '+0.028', '−0.026']
const products = ['0.0022', '0.0014', '0.0025', '0.0036', '0.0008', '0.0015']

// Dimension 288 of the same pair, swapped in over column 3: the only thing that changed
// is that the two signs now disagree, and the term flips from adding to subtracting.
// 43 of the 384 dimensions do this, together worth −0.0069.
const SWAP_COL = 3
const SWAP_AT = 5
const swap = { question: '+0.032', chunk: '−0.035', product: '0.0011' }

// The chart is drawn twice from one set of numbers: first against the whole 0..1 range
// a cosine could occupy, then against the range the corpus actually occupies. Every mark
// is positioned by `at()`, so changing the axis animates them into their new places.
const V = {
  min: 0.661, p1: 0.730, median: 0.800, avg: 0.812, match: 0.887, p99: 0.929, max: 0.999,
}
const ZOOM_AT = 7
const zoomed = computed(() => props.clicks >= ZOOM_AT)
const axis = computed(() => (zoomed.value ? [V.min, V.max] : [0, 1]))
const pct = (v) => {
  const [lo, hi] = axis.value
  return ((v - lo) / (hi - lo)) * 100
}
const at = (v) => `${pct(v).toFixed(2)}%`
const to = (v) => `${(100 - pct(v)).toFixed(2)}%`

const isSwapped = (i) => i === SWAP_COL && props.clicks >= SWAP_AT
const swapIn = (list, key) =>
  computed(() => list.map((v, i) => (isSwapped(i) ? swap[key] : v)))

const questionCells = swapIn(question, 'question')
const chunkCells = swapIn(chunk, 'chunk')
const productCells = swapIn(products, 'product')
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
  padding: 0.38rem 0;
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

/* One shared seven-column grid for values and operators alike, so every ×, ↓ and + sits
   on the centre line of the pair it belongs to. The gap is wide enough to hold the sign
   between two product boxes. */
.cells {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1.1rem;
}
.cell {
  position: relative;
  font-family: var(--font-code);
  font-size: 0.88rem;
  text-align: center;
  border: 2px solid #a8a8a8;
  border-radius: 0.35rem;
  background: #fefefe;
  padding: 0.42rem 0;
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
.cell.swapped {
  border-color: #b23c2c;
}
.cell.product.swapped {
  background: #f7ece9;
  color: #b23c2c;
}

/* Centred on the gutter between two boxes: half the 1.1rem gap, plus the 2px border
   that getBoundingClientRect counts as part of the box. */
.sign {
  position: absolute;
  left: -0.675rem;
  top: 50%;
  transform: translate(-50%, -50%);
  font-family: var(--font-code);
  font-size: 0.95rem;
  font-style: normal;
  font-weight: 700;
  color: #5f6066;
}
.sign.minus { color: #b23c2c; }

.op {
  font-family: var(--font-code);
  font-size: 0.95rem;
  line-height: 1.3;
  text-align: center;
  color: var(--color-primary);
}
.op.down { font-size: 1.05rem; }

/* Both footers occupy the same box, so swapping one for the other moves nothing. */
.calcfoot {
  position: relative;
  height: 2.9rem;
}
.foot {
  position: absolute;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: baseline;
  gap: 1.2rem;
  white-space: nowrap;
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
.verdict {
  font-size: 1.15rem;
  font-weight: 700;
  color: #b23c2c;
}

.scale { padding-top: 1.2rem; }
.stitle {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  color: #1c1c1c;
}
.scount {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  margin: 0.2rem 0 2.8rem;
  color: #5f6066;
}
.bar {
  position: relative;
  height: 2.6rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
}
/* The axis runs from the corpus floor to its ceiling, so the bar ends are the whiskers.
   Positions are computed from the printed values, not from the underlying floats, so the
   marks land where the labels say they do. */
.band {
  position: absolute;
  top: 0;
  bottom: 0;
  background: #edf6ee;
}
.box {
  position: absolute;
  top: 0;
  bottom: 0;
  background: #d9edda;
  border-left: 2px solid #3f8a46;
  border-right: 2px solid #3f8a46;
}

/* Everything on the bar is placed by percentage, so rescaling the axis animates the
   marks into their new positions instead of cutting to them. */
.band, .box, .medline, .mark, .pin, .avglabel, .pinlabel, .tick {
  transition: left 700ms ease, right 700ms ease, transform 700ms ease, opacity 350ms ease;
}
.medline {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 3px;
  background: #276b2e;
}
.mark {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #343434;
}
.pin {
  position: absolute;
  top: -0.4rem;
  bottom: -0.4rem;
  width: 3px;
  background: var(--color-primary);
}
.avglabel {
  position: absolute;
  bottom: 100%;
  transform: translateX(calc(-100% - 6px));
  margin-bottom: 0.5rem;
  font-family: var(--font-code);
  font-size: 0.85rem;
  white-space: nowrap;
  color: #5f6066;
}
.avglabel.wide { transform: translateX(-50%); }
.pinlabel {
  position: absolute;
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
  height: 1.15rem;
  margin-top: 0.35rem;
}
.tick {
  position: absolute;
  transform: translateX(-50%);
  font-family: var(--font-code);
  font-size: 0.8rem;
  color: #5f6066;
}
.tick.min { transform: translateX(0); }
.tick.max { transform: translateX(-100%); }

</style>
