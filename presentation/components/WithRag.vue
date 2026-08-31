<template>
  <div class="with-rag">
    <div class="flow">

      <div class="band">
        <div class="col-retrieval prompt reveal" :class="{ shown: clicks >= 1 }">
          <div class="tag">Prompt</div>
          <div class="prompt-text">when does the bakery close?</div>
        </div>
        <span class="arrow reveal" :class="{ shown: clicks >= 1 }">&larr;</span>
        <div class="actor reveal" :class="{ shown: clicks >= 1 }">
          <ProgrammerGlyph />
          <div class="actor-label">you</div>
        </div>
      </div>

      <div class="band">
        <div class="col-retrieval riser reveal" :class="{ shown: clicks >= 2 }">&darr;</div>
      </div>

      <div class="ragbox reveal" :class="{ shown: clicks >= 2 }">
        <div class="row">
          <div class="step col-retrieval reveal" :class="{ shown: clicks >= 2 }">
            <div class="step-name"><span class="step-letter">R</span>ETRIEVAL</div>
            <div class="step-body">Deterministically query an authoritative source</div>
          </div>

          <span class="arrow reveal" :class="{ shown: clicks >= 3 }">&rarr;</span>

          <div class="step col-augmented reveal" :class="{ shown: clicks >= 3 }">
            <div class="step-name"><span class="step-letter">A</span>UGMENTED PROMPT</div>
            <pre class="step-prompt"><span class="ctx">Bakery De Korenbloem
Mon-Sat  07:00-18:30
Sun + holidays: closed</span>

when does the bakery close?</pre>
          </div>

          <span class="arrow reveal" :class="{ shown: clicks >= 4 }">&rarr;</span>

          <div class="step col-generation reveal" :class="{ shown: clicks >= 4 }">
            <div class="step-name"><span class="step-letter">G</span>ENERATION</div>
            <StochasticParrot />
          </div>
        </div>
      </div>

      <div class="band outro">
        <div class="answer reveal" :class="{ shown: clicks >= 5 }">
          <div class="tag good">Answer</div>
          <div class="answer-text">closed today, it&rsquo;s a holiday</div>
        </div>
        <div class="elbow reveal" :class="{ shown: clicks >= 5 }"><span class="head"></span></div>
      </div>

      <div class="sources reveal" :class="{ shown: clicks >= 6 }">
        Retrieval from:<br>
        <span class="accent">database &middot; web search &middot; wiki &middot; SharePoint &middot; PDFs</span>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.with-rag { text-align: center; }

.flow {
  display: inline-flex;
  flex-direction: column;
  margin: 0 -2.5rem 0 -6rem;
  text-align: initial;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

/* One width for all three boxes. The Prompt shares the retrieval column, so its
   single line has to fit this too — see .prompt-text. */
.col-retrieval,
.col-augmented,
.col-generation { flex: 0 0 16rem; }

/* Matches .ragbox's border + padding so the risers line up with its columns. */
.band {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 calc(0.9rem + 2px);
}
.band.right { justify-content: flex-end; }

/* Elbow out of GENERATION: down its centre line, then left into the Answer.
   The answer is nudged down half its height so it centres on the horizontal. */
.outro {
  justify-content: flex-end;
  align-items: flex-end;
  gap: 1.4rem;
  padding-bottom: 2rem;
}
.outro .answer { transform: translateY(50%); }

/* border-box, so height includes the two legs and `100%` is the outer edge —
   without it the legs sit outside the box the chevron is positioned against. */
.elbow {
  position: relative;
  box-sizing: border-box;
  width: 5rem;
  height: 2.6rem;
  margin-right: calc(8rem - 1px);
  border-right: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
}
/* Open chevron, not a filled triangle, to match the &larr;/&rarr; glyphs. */
.elbow .head {
  position: absolute;
  left: 0;
  top: calc(100% + 1px);
  width: 10px;
  height: 10px;
  box-sizing: border-box;
  border-left: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  transform: translate(-50%, -50%) rotate(45deg);
}

/* Shrink-to-fit, so the arrow sits the same distance from the glyph as from
   the Prompt box instead of floating in a wide empty column. */
.actor { flex: 0 0 auto; text-align: center; }
.actor :deep(svg) { width: 3.2rem; height: auto; margin: 0 auto 0.1rem; }
.actor-label {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #1c1c1c;
}

.arrow {
  font-size: 1.7rem;
  line-height: 1;
  color: var(--color-primary);
}

.riser {
  display: block;
  font-size: 1.2rem;
  line-height: 1.1;
  text-align: center;
  color: var(--color-primary);
}

.tag {
  font-family: var(--font-code);
  font-size: 0.8rem;
  letter-spacing: 0.06em;
  color: #5f6066;
}
.tag.good { color: #276b2e; }

.prompt,
.answer {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  padding: 0.3rem 1rem 0.4rem;
  background: #fefefe;
  box-sizing: border-box;
}
.prompt-text,
.answer-text {
  font-size: 1rem;
  margin-top: 0.15rem;
  color: #1c1c1c;
  white-space: nowrap;
}
/* Sized so the one line fits the shared 16rem column without wrapping. */
.prompt-text { font-family: var(--font-code); font-size: 0.82rem; }
.answer { flex: 0 0 auto; }
.answer.shown {
  border-color: #3f8a46;
  background: #edf6ee;
}

.ragbox {
  border: 2px solid var(--color-primary);
  border-radius: 0.8rem;
  background: #343434;
  padding: 0.45rem 0.9rem 0.55rem;
  box-shadow: 0 10px 26px rgba(232, 71, 0, 0.18);
}

/* stretch keeps all three boxes the same height; space-between puts
   GENERATION's right edge on the box's content edge for the riser below. */
.row {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
}

.step {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  border-radius: 0.55rem;
  background: #fefefe;
  padding: 0.8rem 0.9rem 0.9rem;
  box-sizing: border-box;
}
.row .arrow { align-self: center; padding: 0 0.25rem; }
.step-name {
  font-family: var(--font-heading);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: #1c1c1c;
  text-align: center;
}
.step-letter { color: var(--color-primary); }
.step-body {
  font-size: 0.95rem;
  line-height: 1.4;
  margin-top: 0.3rem;
  color: #33343a;
  text-align: center;
}

.step-prompt {
  font-family: var(--font-code);
  font-size: 0.68rem;
  line-height: 1.25;
  margin: 0.3rem 0 0;
  color: #1c1c1c;
  white-space: pre;
}
.ctx {
  background: #ffe2d2;
  box-shadow: 0 0 0 2px #ffe2d2;
  border-radius: 2px;
  color: #8a2f00;
}

.col-generation :deep(svg) { width: 4.2rem; height: auto; margin: 0.35rem auto 0; }

.sources {
  text-align: center;
  padding-top: 1.6rem;
  font-family: var(--font-code);
  font-size: 0.95rem;
  line-height: 1.6;
  color: #33343a;
}
</style>
