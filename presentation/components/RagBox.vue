<template>
  <div class="rag-box">
    <div class="rag-box-flow">

      <div class="terminal">your<br>question</div>
      <div class="arrow">&rarr;</div>

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
              <div class="slot-desc">find the data<br>that answers this</div>
            </div>
          </div>
          <div class="slot" :class="{ shown: clicks >= 2 }">
            <div class="slot-card"></div>
            <div class="slot-letter">A</div>
            <div class="slot-text">
              <div class="slot-name">Augmented</div>
              <div class="slot-desc">staple it<br>to the question</div>
            </div>
          </div>
          <div class="slot" :class="{ shown: clicks >= 3 }">
            <div class="slot-card"></div>
            <div class="slot-letter">G</div>
            <div class="slot-text">
              <div class="slot-name">Generation</div>
              <div class="slot-desc">hand it all<br>to the LLM</div>
            </div>
          </div>
        </div>
      </div>

      <div class="arrow">&rarr;</div>

      <div class="llm">
        <StochasticParrot />
        <div class="llm-name">LLM</div>
      </div>

      <div class="arrow">&rarr;</div>
      <div class="terminal">your<br>answer</div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.rag-box-flow {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.65rem;
  margin: 1.7rem -2.5rem 0 -6rem;
}

.terminal {
  flex: 0 0 5.6rem;
  text-align: center;
  font-family: var(--font-code);
  font-size: 1rem;
  line-height: 1.4;
  font-weight: 500;
  color: #2f2f2f;
}

.arrow {
  flex: 0 0 auto;
  font-size: 2.1rem;
  line-height: 1;
  color: var(--color-primary);
}

.mystery {
  position: relative;
  overflow: hidden;
  flex: 0 0 auto;
  border-radius: 0.9rem;
  padding: 1rem 1.1rem 1.4rem;
  background: #343434;
  border: 2px solid #343434;
  transition: border-color 500ms ease, box-shadow 500ms ease;
}
.mystery.opened {
  border-color: var(--color-primary);
  box-shadow: 0 10px 26px rgba(232, 71, 0, 0.2);
}

.marks {
  position: absolute;
  inset: 0;
  pointer-events: none;
  transition: opacity 500ms ease;
}
.mystery.opened .marks { opacity: 0; }
.m {
  position: absolute;
  font-family: var(--font-heading);
  font-weight: 700;
  color: #fefefe;
}
.m1 { top: 8%;  left: 6%;  font-size: 5rem;   opacity: 0.05; transform: rotate(-14deg); }
.m2 { top: 46%; left: 27%; font-size: 8rem;   opacity: 0.04; transform: rotate(9deg); }
.m3 { top: 4%;  left: 52%; font-size: 6.5rem; opacity: 0.05; transform: rotate(18deg); }
.m4 { top: 52%; left: 68%; font-size: 4.5rem; opacity: 0.06; transform: rotate(-8deg); }
.m5 { top: 18%; left: 84%; font-size: 7rem;   opacity: 0.04; transform: rotate(12deg); }
.m6 { top: 60%; left: 3%;  font-size: 4rem;   opacity: 0.05; transform: rotate(6deg); }

.mystery-title {
  position: relative;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.16em;
  color: #8d8d8d;
  margin-bottom: 0.7rem;
  transition: color 500ms ease;
}
.mystery.opened .mystery-title { color: #c9c9c9; }

.mystery-slots {
  position: relative;
  display: flex;
  gap: 0.75rem;
}

.slot {
  position: relative;
  flex: 0 0 7.7rem;
  height: 13rem;
  padding-top: 1.7rem;
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
.slot.shown .slot-card {
  opacity: 1;
  transform: none;
}

.slot-letter {
  position: relative;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 5rem;
  line-height: 1;
  color: var(--color-primary-muted);
  transition: color 400ms ease;
}
.slot.shown .slot-letter { color: var(--color-primary); }

.slot-text {
  position: relative;
  margin-top: 0.7rem;
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
  line-height: 1.45;
  margin-top: 0.35rem;
  color: #5b5c62;
}

.llm {
  flex: 0 0 7.8rem;
  text-align: center;
}
.llm :deep(.parrot) {
  width: 6.4rem;
  height: auto;
  margin: 0 auto 0.4rem;
}
.llm-name {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #232323;
}
.llm-desc {
  font-size: 0.8rem;
  line-height: 1.45;
  margin-top: 0.35rem;
  color: #5b5c62;
}

.rag-kicker {
  text-align: center;
  margin: 2.6rem -2.5rem 0 -6rem;
  font-size: 1.15rem;
  color: #2f2f2f;
  opacity: 0;
  transition: opacity 400ms ease;
}
.rag-kicker.shown { opacity: 1; }
.rag-kicker b { color: var(--color-primary); }
</style>
