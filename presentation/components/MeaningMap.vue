<template>
  <div class="meaning-map">
    <div class="plane">

      <svg class="lines" viewBox="0 0 100 100" preserveAspectRatio="none">
        <line
          class="near reveal" :class="{ shown: clicks === 2 }"
          x1="19" y1="26" x2="32" y2="14"
        />
        <line
          class="far reveal" :class="{ shown: clicks === 2 }"
          x1="19" y1="26" x2="44" y2="76"
        />
        <line
          v-for="p in nearest" :key="p.x"
          class="hit reveal" :class="{ shown: clicks >= 3 }"
          x1="36" y1="37" :x2="p.x" :y2="p.y"
        />
      </svg>

      <div
        v-for="p in points"
        :key="p.label"
        class="pt reveal"
        :class="[p.side, { shown: clicks >= 1 }]"
        :style="{ left: p.x + '%', top: p.y + '%' }"
      >
        <span class="dot"></span>
        <span class="label">{{ p.label }}</span>
      </div>

      <div class="pt query reveal" :class="{ shown: clicks >= 3 }" style="left: 36%; top: 37%">
        <span class="dot"></span>
      </div>

      <div class="query-label reveal" :class="{ shown: clicks >= 3 }">wie kent container orchestration?</div>

      <div class="verdict near-label reveal" :class="{ shown: clicks === 2 }">near = similar</div>
      <div class="verdict far-label reveal" :class="{ shown: clicks === 2 }">far = different</div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Placed by hand, not projected. The real projection is the app's job — this one only
// has to be big enough to read from the back of the room.
const points = [
  { x: 32, y: 14, label: 'Docker', side: 'right' },
  { x: 19, y: 26, label: 'Kubernetes', side: 'right' },
  { x: 13, y: 58, label: 'CI/CD pipelines', side: 'right' },
  { x: 72, y: 22, label: 'React', side: 'left' },
  { x: 84, y: 40, label: 'Angular', side: 'left' },
  { x: 44, y: 76, label: 'opleidingsbudget', side: 'right' },
  { x: 62, y: 90, label: 'wagenpolicy', side: 'right' },
]

const nearest = [
  { x: 19, y: 26 },
  { x: 32, y: 14 },
  { x: 13, y: 58 },
]
</script>

<style scoped>
.meaning-map { margin-top: 1.2rem; }

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.plane {
  position: relative;
  height: 26rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
}

.lines {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}
.lines line {
  fill: none;
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}
.lines .near { stroke: #3f8a46; }
.lines .far { stroke: #a8a8a8; stroke-dasharray: 6 5; }
.lines .hit { stroke: var(--color-primary); }

/* A zero-size anchor sitting exactly on the point. The dot and label are placed
   against it with margins rather than a percentage transform, so a dot lands on its
   coordinate whatever the inherited line-height happens to be — the lines drawn
   between points depend on it. */
.pt {
  position: absolute;
  width: 0;
  height: 0;
}

.dot {
  position: absolute;
  left: -0.4rem;
  top: -0.4rem;
  width: 0.8rem;
  height: 0.8rem;
  border-radius: 50%;
  background: #343434;
}
.label {
  position: absolute;
  left: 0.75rem;
  top: 0;
  transform: translateY(-50%);
  font-size: 1.1rem;
  line-height: 1.2;
  white-space: nowrap;
  color: #33343a;
}
.pt.left .label {
  left: auto;
  right: 0.75rem;
}

/* The marker is the dot alone, so it centres on its coordinate exactly like every
   other point; the label hangs off it down and to the right, the one quadrant none of
   the three nearest-neighbour lines runs through. */
.query-label {
  position: absolute;
  left: 37.5%;
  top: 40%;
  font-size: 1.1rem;
  font-weight: 700;
  white-space: nowrap;
  color: var(--color-primary);
}

/* The question is put on the same map with the same model — that is the whole of
   vector search, and it lands here without sharing a word with anything near it. */
.query .dot {
  left: -0.525rem;
  top: -0.525rem;
  width: 1.05rem;
  height: 1.05rem;
  background: var(--color-primary);
  box-shadow: 0 0 0 4px #fefefe;
}

.verdict {
  position: absolute;
  font-family: var(--font-code);
  font-size: 0.9rem;
  letter-spacing: 0.03em;
  white-space: nowrap;
  border-radius: 0.4rem;
  padding: 0.25rem 0.6rem;
}
.near-label {
  left: 4.5%;
  top: 12%;
  color: #276b2e;
  background: #edf6ee;
  border: 2px solid #3f8a46;
}
.far-label {
  left: 36%;
  top: 47%;
  color: #5f6066;
  background: #f4f4f4;
  border: 2px solid #a8a8a8;
}
</style>
