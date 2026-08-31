<template>
  <div class="context-window">

    <div class="rail-wrap">

      <div class="above">
        <div class="needle-note reveal" :class="{ shown: clicks >= 3 }">
          <div class="needle-title">LOST IN THE MIDDLE</div>
          <div class="needle-text">the answer is in here somewhere...</div>
          <span class="drop"></span>
        </div>
        <div class="scale">context window <span class="tokens">1M tokens</span></div>
      </div>

      <div class="rail">
        <div class="fill reveal" :class="{ shown: clicks >= 1 }"></div>
        <div class="growth reveal" :class="{ shown: clicks >= 4 }"></div>
        <div class="sliver reveal" :class="{ shown: clicks >= 2 }"></div>
        <div class="needle reveal" :class="{ shown: clicks >= 3 }"></div>
        <div class="tail reveal" :class="{ shown: clicks >= 4 }"></div>
        <div class="tail-note reveal" :class="{ shown: clicks >= 4 }">40 consultants &rarr; 400</div>
      </div>

      <div class="notes">
        <div class="note note-corpus reveal" :class="{ shown: clicks >= 1 }">
          <span class="elbow"></span>
          <span class="txt">40 CVs &middot; 20 Policy PDFs <span class="tokens">220k tokens</span><span class="cost">$1.10</span></span>
        </div>
        <div class="note note-rag reveal" :class="{ shown: clicks >= 2 }">
          <span class="elbow"></span>
          <span class="txt"><span class="kicker">with embeddings</span> 5 retrieved chunks <span class="tokens">500 tokens</span><span class="cost">$0.0025</span></span>
        </div>
      </div>

    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
/* Everything on this slide is positioned against one horizontal scale: the rail is
   the 1M-token context window, and --corpus is 224 245 of those tokens. Change the
   token counts and only this one number moves. */
.context-window {
  --corpus: 22%;
  --needle: 12%;
  width: 100%;
  margin-top: 2rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

/* Room to the right of the rail for the overflow tail to run off the window. */
.rail-wrap {
  position: relative;
  margin-right: 6rem;
}

.above {
  position: relative;
  height: 6.8rem;
}
.scale {
  position: absolute;
  right: 0;
  bottom: 0.35rem;
  font-family: var(--font-code);
  font-size: 0.95rem;
  letter-spacing: 0.03em;
  color: #5f6066;
}

.needle-note {
  position: absolute;
  left: var(--needle);
  bottom: 0.4rem;
  transform: translateX(-1.2rem);
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.45rem 0.9rem 0.55rem;
  white-space: nowrap;
}
.needle-title {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: #276b2e;
}
.needle-text {
  font-size: 1.1rem;
  margin-top: 0.1rem;
  color: #33343a;
}
.needle-note .drop {
  position: absolute;
  left: calc(1.2rem - 1px);
  top: calc(100% + 2px);
  width: 0;
  height: 0.4rem;
  border-left: 2px solid #276b2e;
}

.rail {
  position: relative;
  height: 5.6rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
  overflow: visible;
}

.fill {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: var(--corpus);
  border-radius: 0.25rem 0 0 0.25rem;
  background: #343434;
}

/* The same corpus at ten times the headcount. Striped rather than solid so it
   reads as projected, and it runs under .tail off the right-hand edge. */
.growth {
  position: absolute;
  left: var(--corpus);
  top: 0;
  bottom: 0;
  right: 0;
  background: repeating-linear-gradient(
    -45deg,
    #343434 0 6px,
    #fefefe 6px 12px
  );
}
.tail {
  position: absolute;
  left: 100%;
  top: -2px;
  bottom: -2px;
  width: 6rem;
  background: repeating-linear-gradient(
    -45deg,
    #343434 0 6px,
    #fefefe 6px 12px
  );
  mask-image: linear-gradient(to right, #000 45%, transparent 100%);
}
/* Right-aligned and dropped below the corpus label, so the overflow tail can run
   toward the slide edge without its caption running off it. */
.tail-note {
  position: absolute;
  left: auto;
  right: -3.2rem;
  top: calc(100% + 5.2rem);
  text-align: right;
  font-family: var(--font-code);
  font-size: 0.9rem;
  white-space: nowrap;
  color: #33343a;
}

/* 500 tokens is 0.05% of the rail — a hairline, not a sub-pixel sliver. */
.sliver {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 0.25rem 0 0 0.25rem;
  background: var(--color-primary);
}

.needle {
  position: absolute;
  left: var(--needle);
  top: 50%;
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  background: #3f8a46;
  box-shadow: 0 0 0 3px #fefefe;
}

.notes {
  position: relative;
  height: 9rem;
  margin: 0 2px;
}
.note {
  position: absolute;
  top: 0;
  display: flex;
  align-items: flex-end;
}
/* Down from the rail, then right into the label — the same open elbow the
   arrows elsewhere in the deck use. */
.note .elbow {
  flex: 0 0 auto;
  box-sizing: border-box;
  width: 1.1rem;
  border-left: 2px solid #a8a8a8;
  border-bottom: 2px solid #a8a8a8;
}
.note .txt {
  font-size: 1.15rem;
  line-height: 1;
  padding-left: 0.6rem;
  transform: translateY(0.35rem);
  white-space: nowrap;
  color: #33343a;
}
.kicker {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding-right: 0.4rem;
  color: #5f6066;
}
/* Charcoal by default; the retrieved-chunks badge takes the colour of its sliver. */
.tokens {
  font-family: var(--font-code);
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem 0.25rem;
  margin-left: 0.6rem;
  border-radius: 0.35rem;
  background: #343434;
  color: #fefefe;
}

.note-corpus { left: var(--corpus); }
.note-corpus .elbow { height: 3rem; }

.note-rag { left: 0; }
.note-rag .elbow { height: 7rem; }
.note-rag .elbow { border-color: var(--color-primary); }
.note-rag .tokens { background: var(--color-primary); }

/* The price rides with the token count rather than on its own click. */
.cost {
  font-family: var(--font-code);
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem 0.25rem;
  margin-left: 0.35rem;
  border-radius: 0.35rem;
  border: 2px solid #343434;
  background: #fefefe;
  color: #343434;
}
.note-rag .cost {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
