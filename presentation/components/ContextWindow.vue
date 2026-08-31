<template>
  <div class="context-window">

    <div class="rail-wrap">

      <div class="above">
        <div class="needle-note reveal" :class="{ shown: clicks >= 4 }">
          the answer is in here somewhere
          <span class="drop"></span>
        </div>
        <div class="scale">context window <b>1 000 000 tokens</b></div>
      </div>

      <div class="rail">
        <div class="fill reveal" :class="{ shown: clicks >= 1 }"></div>
        <div class="growth reveal" :class="{ shown: clicks >= 5 }"></div>
        <div class="sliver reveal" :class="{ shown: clicks >= 2 }"></div>
        <div class="needle reveal" :class="{ shown: clicks >= 4 }"></div>
        <div class="tail reveal" :class="{ shown: clicks >= 5 }"></div>
        <div class="tail-note reveal" :class="{ shown: clicks >= 5 }">40 consultants &rarr; 400</div>
      </div>

      <div class="notes">
        <div class="note note-corpus reveal" :class="{ shown: clicks >= 1 }">
          <span class="elbow"></span>
          <span class="txt">37 CVs &middot; 20 policy PDFs &middot; credits ledger <b>224 245 tokens</b></span>
        </div>
        <div class="note note-rag reveal" :class="{ shown: clicks >= 2 }">
          <span class="elbow"></span>
          <span class="txt">5 retrieved chunks <b>500 tokens</b></span>
        </div>
      </div>

    </div>

    <div class="prices reveal" :class="{ shown: clicks >= 3 }">
      <div class="price">$1.12 <span class="per">/ question</span></div>
      <div class="ratio"><span class="rule"></span><span class="badge">450&times;</span><span class="rule"></span></div>
      <div class="price good">$0.0025 <span class="per">/ question</span></div>
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
  --corpus: 22.4%;
  --needle: 12.3%;
  width: 100%;
  margin-top: 1.6rem;
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
  height: 3.6rem;
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
.scale b { color: #1c1c1c; font-weight: 600; }

.needle-note {
  position: absolute;
  left: var(--needle);
  bottom: 0.35rem;
  transform: translateX(-1.2rem);
  font-size: 1.1rem;
  white-space: nowrap;
  color: #33343a;
}
.needle-note .drop {
  position: absolute;
  left: 1.2rem;
  top: 100%;
  width: 0;
  height: 0.35rem;
  border-left: 2px solid #276b2e;
}

.rail {
  position: relative;
  height: 5rem;
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
  top: calc(100% + 4.5rem);
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
  height: 7.4rem;
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
.note .txt b {
  font-family: var(--font-code);
  font-size: 1.05rem;
  font-weight: 600;
  padding-left: 0.55rem;
  color: #1c1c1c;
}

.note-corpus { left: var(--corpus); }
.note-corpus .elbow { height: 2.6rem; }

.note-rag { left: 0; }
.note-rag .elbow { height: 6rem; }
.note-rag .elbow { border-color: var(--color-primary); }
.note-rag .txt b { color: var(--color-primary); }

.prices {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.8rem;
  padding-top: 3.2rem;
}
.price {
  font-family: var(--font-code);
  font-size: 2.1rem;
  font-weight: 600;
  color: #1c1c1c;
}
.price.good { color: #276b2e; }
.price .per {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 400;
  padding-left: 0.4rem;
  color: #5f6066;
}

.ratio {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.ratio .rule {
  width: 3.6rem;
  border-top: 2px dashed #a8a8a8;
}
.ratio .badge {
  font-family: var(--font-heading);
  font-size: 1.9rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-primary);
}
</style>
