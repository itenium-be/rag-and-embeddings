<template>
  <div class="without-rag">
    <div class="stage">

      <div class="actors">
        <div class="actor">
          <ProgrammerGlyph />
          <div class="actor-label">You</div>
        </div>

        <div class="link">
          <div class="wire-label">when does the bakery close?</div>
          <div class="wire-line"></div>
        </div>

        <div class="actor">
          <StochasticParrot />
          <div class="actor-label">LLM</div>
        </div>
      </div>

      <div class="issues">
        <div class="issue" :class="{ shown: clicks >= 1 }">
          <div class="issue-title">Hallucinations</div>
          <div class="issue-body">Is that answer correct?<br>Who knows!</div>
        </div>
        <div class="issue" :class="{ shown: clicks >= 2 }">
          <div class="issue-title">Training Cutoff</div>
          <div class="issue-body">The actual opening hours have changed</div>
        </div>
        <div class="issue" :class="{ shown: clicks >= 3 }">
          <div class="issue-title">Missing Context</div>
          <div class="issue-body">Today is a Belgian holiday</div>
        </div>
      </div>

      <div class="sep" :class="{ shown: clicks >= 4 }">
        <span class="sep-line"></span>
        <span class="sep-label">other issues</span>
        <span class="sep-line"></span>
      </div>

      <div class="issues centered">
        <div class="issue" :class="{ shown: clicks >= 5 }">
          <div class="issue-title">Private Information</div>
          <div class="issue-body">Your internal portal is not in its training data. It does not know when the helpdesk closes</div>
        </div>
        <div class="issue" :class="{ shown: clicks >= 6 }">
          <div class="issue-title">Lack of Understanding</div>
          <div class="issue-body">&ldquo;Agile&rdquo; in here does not mean what it means out there</div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.without-rag { text-align: center; }

.stage {
  display: inline-flex;
  flex-direction: column;
  width: 52rem;
  margin: 0.4rem -2.5rem 0 -6rem;
  text-align: initial;
}

.actors {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actor { flex: 0 0 10.8rem; text-align: center; }
.actor :deep(svg) { width: 5.8rem; height: auto; margin: 0 auto 0.25rem; }
.actor-label {
  font-family: var(--font-code);
  font-size: 1.05rem;
  font-weight: 500;
  color: #232323;
}

.link { flex: 1; padding: 0 1rem; }
.wire-label {
  font-family: var(--font-code);
  font-size: 1rem;
  text-align: center;
  margin-bottom: 0.4rem;
  color: #2f2f2f;
}
.wire-line {
  position: relative;
  height: 2px;
  background: var(--color-primary);
}
.wire-line::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  border-top: 7px solid transparent;
  border-bottom: 7px solid transparent;
  border-left: 11px solid var(--color-primary);
}

.issues {
  display: flex;
  gap: 1rem;
  margin-top: 1.4rem;
}
.issues.centered { justify-content: center; }

/* Fixed basis, not 1fr, so the two rows of cards come out the same width. */
.issue {
  flex: 0 0 16.66rem;
  min-height: 6.1rem;
  box-sizing: border-box;
  border: 2px solid #e0cbc6;
  border-top: 4px solid #b23c2c;
  border-radius: 0.6rem;
  padding: 0.7rem 0.85rem 0.8rem;
  background: #fefefe;
  opacity: 0;
  transform: translateY(0.5rem);
  transition: opacity 400ms ease, transform 400ms ease;
}
.issue.shown { opacity: 1; transform: none; }

.issue-title {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 500;
  color: #b23c2c;
}
.issue-body {
  font-size: 0.85rem;
  line-height: 1.4;
  margin-top: 0.35rem;
  color: #5b5c62;
}

.sep {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  margin-top: 1.5rem;
  opacity: 0;
  transition: opacity 400ms ease;
}
.sep.shown { opacity: 1; }
.sep-line {
  flex: 1;
  height: 1px;
  background: #d5d5d5;
}
.sep-label {
  font-family: var(--font-code);
  font-size: 0.9rem;
  letter-spacing: 0.08em;
  color: #8d8d8d;
}
</style>
