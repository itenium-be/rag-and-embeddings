<template>
  <div class="context-window">

    <div class="rail-wrap">

      <div class="above">
        <div class="scale">context window <span class="tokens">1M tokens</span></div>
      </div>

      <div class="rail">
        <div class="fill reveal" :class="{ shown: clicks >= 1 }"></div>
        <div class="growth reveal" :class="{ shown: clicks >= 3 }"></div>
        <div class="window-edge"></div>
        <div class="sliver reveal" :class="{ shown: clicks >= 5 }"></div>
        <div class="needle reveal" :class="{ shown: clicks >= 2 }"></div>
        <div class="link-needle reveal" :class="{ shown: clicks === 2 }"></div>
      </div>

      <div class="notes">
        <!-- The size problem replaces the corpus line in place, so the leader keeps
             pointing at the spot where the real corpus ends and the extra begins. -->
        <div class="note note-corpus reveal" :class="{ shown: clicks === 1 || clicks === 2 }">
          <span class="elbow"></span>
          <span class="txt">40 CVs &middot; 20 Policy PDFs <span class="tokens">220k tokens</span></span>
        </div>

        <div class="note note-corpus reveal" :class="{ shown: clicks >= 3 }">
          <span class="elbow"></span>
          <span class="txt">400 CVs &middot; 200 PDFs <span class="tokens">2.2M tokens</span><span
            class="cost reveal" :class="{ shown: clicks >= 4 }"
          >$11.00<span class="link-cost reveal" :class="{ shown: clicks === 4 }"></span></span>
            <span class="brace reveal" :class="{ shown: clicks === 3 }">
              <svg viewBox="0 0 100 8" preserveAspectRatio="none">
                <path
                  d="M0,0 Q0,3 2,3 L47,3 Q50,3 50,8 Q50,3 53,3 L98,3 Q100,3 100,0"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  vector-effect="non-scaling-stroke"
                />
              </svg>
              <span class="brace-stem"></span>
            </span></span>
        </div>

        <div class="note note-rag reveal" :class="{ shown: clicks >= 5 }">
          <span class="elbow"></span>
          <span class="txt"><span class="kicker">embeddings</span> 5 retrieved chunks <span class="tokens">500 tokens</span><span class="cost">$0.0025</span></span>
        </div>

      </div>

    </div>

    <div class="verdicts">
      <div class="card problem reveal" :class="{ shown: clicks >= 2 }">
        <div class="card-kicker">PROBLEM 1</div>
        <div class="card-title">LOST IN THE MIDDLE</div>
        <div class="card-body">The answer is in here somewhere...</div>
      </div>
      <div class="card problem reveal" :class="{ shown: clicks >= 3 }">
        <div class="card-kicker">PROBLEM 2</div>
        <div class="card-title">SCALE</div>
        <div class="card-body">What if 400 consultants, 200 PDFs?</div>
      </div>
      <div class="card problem reveal" :class="{ shown: clicks >= 4 }">
        <div class="card-kicker">PROBLEM 3</div>
        <div class="card-title">MONEY</div>
        <div class="card-body">You pay for all of it, every question</div>
      </div>
      <div class="card solution reveal" :class="{ shown: clicks >= 5 }">
        <div class="card-kicker">SOLUTION</div>
        <div class="card-title">EMBEDDINGS</div>
        <div class="card-body">Split text up in chunks and turn each into a vector</div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
/* Everything on this slide is positioned against one horizontal scale: the rail is
   the 1M-token context window, and --corpus is 220k of those tokens. Change the
   token counts and only this one number moves.
   --notes-h is shared by the connectors, which all run from something on the bar
   down to the card row and so need to know how far that is. */
.context-window {
  --corpus: 22%;
  --needle: 12%;
  --notes-h: 9rem;
  width: 100%;
  margin-top: 1rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

/* Room to the right of the rail for the overflowing bar to run off the window. */
.rail-wrap {
  position: relative;
  margin-right: 6rem;
}

.above {
  position: relative;
  height: 2.4rem;
}
.scale {
  position: absolute;
  right: 0;
  bottom: 0.3rem;
  font-family: var(--font-code);
  font-size: 0.95rem;
  letter-spacing: 0.03em;
  color: #5f6066;
}

.rail {
  position: relative;
  height: 5.4rem;
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

/* Ten times the corpus. One element rather than one inside the rail and one past
   it, because a second gradient restarts its phase and the stripes jog at the seam. */
.growth {
  position: absolute;
  left: var(--corpus);
  top: 0;
  bottom: 0;
  /* Runs past the layout's padding and off the slide: the bar does not stop, the
     screen does. */
  right: -10rem;
  background: repeating-linear-gradient(
    -45deg,
    #343434 0 6px,
    #fefefe 6px 12px
  );
  /* Solid inside the window, dissolving over the run from the window's edge to
     the screen's — the bar does not stop, it goes out of view. */
  mask-image: linear-gradient(to right, #000 77%, transparent 97%);
}

/* The bar paints over the rail's right border on its way out, so the edge of the
   context window is drawn back on top of it. */
.window-edge {
  position: absolute;
  right: -2px;
  top: -2px;
  bottom: -2px;
  width: 2px;
  background: #a8a8a8;
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
  background: #b23c2c;
  box-shadow: 0 0 0 3px #fefefe;
}

/* Dot down to its card. Hung off the rail rather than the dot so it starts at the
   bar's edge instead of behind the dot's white ring. */
.link-needle {
  position: absolute;
  left: var(--needle);
  top: 100%;
  height: var(--notes-h);
  border-left: 2px solid #b23c2c;
}

.notes {
  position: relative;
  height: var(--notes-h);
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
  position: relative;
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

/* Charcoal by default; the retrieved-chunks badges take the colour of their sliver. */
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
.cost {
  position: relative;
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

/* Money badge down to its card. Anchored inside the badge so it stays centred on
   it however wide the row's text runs. */
.link-cost {
  position: absolute;
  left: 50%;
  top: calc(100% + 2px);
  height: calc(var(--notes-h) - 4rem);
  border-left: 2px solid #b23c2c;
}

.note-corpus { left: var(--corpus); }
.note-corpus .elbow { height: 2.4rem; }

.note-rag { left: 0; }
.note-rag .elbow { height: 7.4rem; border-color: var(--color-primary); }
.note-rag .tokens { background: var(--color-primary); }
.note-rag .cost { border-color: var(--color-primary); color: var(--color-primary); }

/* Hung off the row's text so it spans exactly that row; the stem carries its
   centre spike down to the card. */
.brace {
  position: absolute;
  left: 0.6rem;
  /* Stops at the token badge: the price badge is still transparent on this click
     but already holds its space, and the brace should not span empty room. */
  right: 4.4rem;
  top: calc(100% + 0.5rem);
  color: #b23c2c;
}
.brace svg {
  display: block;
  width: 100%;
  height: 0.8rem;
  overflow: visible;
}
.brace-stem {
  position: absolute;
  left: 50%;
  top: 0.8rem;
  height: calc(var(--notes-h) - 4rem);
  border-left: 2px solid #b23c2c;
}

.verdicts {
  display: flex;
  align-items: stretch;
  gap: 1rem;
  padding-top: 0.2rem;
}
.card {
  flex: 1;
  border: 2px solid #e0cbc6;
  border-top: 4px solid #b23c2c;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.55rem 0.9rem 0.7rem;
}
.card.solution {
  border-color: #cfe3d1;
  border-top-color: #3f8a46;
  background: #f4faf5;
}
.card-kicker {
  font-family: var(--font-code);
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  color: #b23c2c;
}
.card.solution .card-kicker { color: #276b2e; }
.card-title {
  font-family: var(--font-heading);
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  margin-top: 0.1rem;
  color: #1c1c1c;
}
.card-body {
  font-size: 0.95rem;
  line-height: 1.3;
  margin-top: 0.25rem;
  color: #33343a;
}
</style>
