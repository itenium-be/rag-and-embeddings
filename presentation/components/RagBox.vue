<template>
  <div class="rag-box">
    <div class="stage">

      <div class="mystery" :class="{ opened: clicks >= 1 }">
          <div class="marks" aria-hidden="true">
            <span class="m m1">?</span>
            <span class="m m2">?</span>
            <span class="m m3">?</span>
            <span class="m m4">?</span>
            <span class="m m5">?</span>
            <span class="m m6">?</span>
          </div>
          <div class="mystery-slots">
            <div class="slot" :class="{ shown: clicks >= 1 }">
              <div class="slot-card"></div>
              <div class="slot-letter">R</div>
              <div class="slot-text">
                <div class="slot-name">Retrieval</div>
                <div class="slot-desc">find the data that answers it</div>
              </div>
            </div>
            <div class="slot" :class="{ shown: clicks >= 2 }">
              <div class="slot-card"></div>
              <div class="slot-letter">A</div>
              <div class="slot-text">
                <div class="slot-name">Augmented</div>
                <div class="slot-desc">staple it to the question</div>
              </div>
            </div>
            <div class="slot" :class="{ shown: clicks >= 3 }">
              <div class="slot-card"></div>
              <div class="slot-letter">G</div>
              <div class="slot-text">
                <div class="slot-name">Generation</div>
                <div class="slot-desc">hand it all to the LLM</div>
              </div>
            </div>
          </div>
      </div>

      <div class="risers">
        <div class="riser"><span class="arrow">&uarr;</span></div>
        <div class="riser"><span class="arrow">&darr;</span></div>
      </div>

      <div class="actors">
        <div class="actor">
          <ProgrammerGlyph />
          <div class="actor-label"><span class="caret">&gt;</span> question</div>
        </div>
        <div class="link">
          <div class="link-label">answer</div>
          <div class="link-line"></div>
        </div>
        <div class="actor">
          <StochasticParrot />
          <div class="actor-label">LLM</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.rag-box { text-align: center; }

/* Shrinks to the .mystery's width, so the rows below can be 100% wide and stay
   locked to the box's edges. */
.stage {
  display: inline-flex;
  flex-direction: column;
  margin: 0.7rem -2.5rem 0 -6rem;
}

/* The padding clears the .mystery border + padding, so these rows span exactly
   the slot strip: space-between then lands the outer children on R and G. */
.risers,
.actors {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  box-sizing: border-box;
  padding: 0 calc(1.1rem + 2px);
}

.riser,
.actor { flex: 0 0 10.8rem; text-align: center; }

.arrow {
  font-size: 2.2rem;
  line-height: 1;
  color: var(--color-primary);
}

.mystery {
  position: relative;
  overflow: hidden;
  border-radius: 0.9rem;
  padding: 0.85rem 1.1rem 1rem;
  background: #343434;
  border: 2px solid #343434;
  transition: border-color 500ms ease, box-shadow 500ms ease;
}
.mystery.opened {
  border-color: var(--color-primary);
  box-shadow: 0 10px 26px rgba(232, 71, 0, 0.2);
}

.marks { position: absolute; inset: 0; pointer-events: none; transition: opacity 500ms ease; }
.mystery.opened .marks { opacity: 0; }
.m {
  position: absolute;
  font-family: var(--font-heading);
  font-weight: 700;
  color: #fefefe;
}
.m1 { top: 6%;  left: 5%;  font-size: 5rem;   opacity: 0.13; transform: rotate(-14deg); }
.m2 { top: 44%; left: 25%; font-size: 8rem;   opacity: 0.10; transform: rotate(9deg); }
.m3 { top: 2%;  left: 50%; font-size: 6.5rem; opacity: 0.12; transform: rotate(18deg); }
.m4 { top: 50%; left: 68%; font-size: 4.5rem; opacity: 0.15; transform: rotate(-8deg); }
.m5 { top: 14%; left: 85%; font-size: 7rem;   opacity: 0.11; transform: rotate(12deg); }
.m6 { top: 58%; left: 2%;  font-size: 4rem;   opacity: 0.13; transform: rotate(6deg); }

.mystery-title {
  position: relative;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: 0.16em;
  color: #8d8d8d;
  margin-bottom: 0.6rem;
  transition: color 500ms ease;
}
.mystery.opened .mystery-title { color: #c9c9c9; }

.mystery-slots { position: relative; display: flex; gap: 0.75rem; }

/* No fixed height: .slot-text stays in flow while hidden, so the slot keeps one
   size across every click and .slot-card (inset 0) always covers the text. */
.slot {
  position: relative;
  flex: 0 0 10.8rem;
  padding: 1.2rem 0 1.3rem;
  text-align: center;
}
.slot-card {
  position: absolute;
  inset: 0;
  border-radius: 0.6rem;
  background: #fefefe;
  opacity: 0;
  transform: scale(0.96);
  transition: opacity 400ms ease, transform 400ms ease;
}
.slot.shown .slot-card { opacity: 1; transform: none; }

.slot-letter {
  position: relative;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 4.4rem;
  line-height: 1;
  color: var(--color-primary-muted);
  transition: color 400ms ease;
}
.slot.shown .slot-letter { color: var(--color-primary); }

.slot-text {
  position: relative;
  margin-top: 0.5rem;
  padding: 0 0.6rem;
  opacity: 0;
  transition: opacity 400ms ease 120ms;
}
.slot.shown .slot-text { opacity: 1; }

.slot-name {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 500;
  color: #232323;
}
.slot-desc {
  font-size: 0.8rem;
  line-height: 1.4;
  margin-top: 0.3rem;
  color: #5b5c62;
}

.actor :deep(svg) { width: 8rem; height: auto; margin: 0 auto 0.3rem; }
.actor-label {
  font-family: var(--font-code);
  font-size: 1.1rem;
  font-weight: 500;
  color: #232323;
}
.caret { color: var(--color-primary); }

.link { flex: 1; padding: 0 1.2rem; }
.link-label {
  font-family: var(--font-code);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--color-primary);
  margin-bottom: 0.45rem;
}
.link-line {
  position: relative;
  height: 2px;
  background: var(--color-primary);
}
.link-line::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-right: 11px solid var(--color-primary);
}
</style>
