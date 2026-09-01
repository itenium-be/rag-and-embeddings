<template>
  <div class="prod">

    <div class="box wide reveal" :class="{ shown: clicks >= 1 }">
      <div class="name">Evals</div>
      <div class="inner">
        <div class="chip">
          <div class="chip-name">Golden dataset</div>
          <div class="chip-sub">Questions, the right answer, the documents it must come from</div>
        </div>
        <div class="arrow">&rarr;</div>
        <div class="chip">
          <div class="chip-name">Judge</div>
          <div class="chip-sub">Scores every answer against it, every time you change something</div>
        </div>
      </div>
      <div class="badge on">running all session</div>
    </div>

    <div class="box reveal" :class="{ shown: clicks >= 2 }">
      <div class="name">Guardrails</div>
      <div class="sub">
        Refuse when the sources do not answer. Check that the citation
        holds up the claim it is attached to.
      </div>
      <div class="badge on">the refusal, not the check</div>
    </div>

    <div class="box reveal" :class="{ shown: clicks >= 3 }">
      <div class="name">Ingestion</div>
      <div class="sub">
        Parse, strip what may not be stored, re-index what changed,
        version it so a bad run can be rolled back.
      </div>
      <div class="badge on">no re-index, no versions</div>
    </div>

    <div class="box reveal" :class="{ shown: clicks >= 4 }">
      <div class="name">Observability</div>
      <div class="sub">
        Every question, the chunks it retrieved, what it cost and how long
        it took &mdash; kept, not printed and lost.
      </div>
      <div class="badge on">printed and lost</div>
    </div>

    <div class="box reveal" :class="{ shown: clicks >= 5 }">
      <div class="name">Caching</div>
      <div class="sub">
        The embeddings, the prompts, and the one that bites:
        answering a question because a similar one was asked.
      </div>
      <div class="badge on">prompts only</div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.prod {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 0.9rem;
  height: 27.4rem;
  grid-template-rows: 1fr 1fr;
}

/* Nothing is ever dimmed: unrevealed boxes are fully transparent and keep their
   space, so the grid never reflows. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.box {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  background: #fefefe;
  padding: 0.9rem 1.1rem 0.75rem;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.box.wide { grid-column: span 2; }

.name {
  font-family: var(--font-heading);
  font-size: 1.3rem;
  font-weight: 700;
  color: #1c1c1c;
}

.sub {
  font-size: 1.05rem;
  line-height: 1.35;
  color: #33343a;
  margin-top: 0.3rem;
}

.inner {
  display: flex;
  align-items: stretch;
  gap: 0.55rem;
  margin-top: 0.4rem;
}
.chip {
  flex: 1;
  border: 2px solid #a8a8a8;
  border-left: 5px solid var(--color-primary);
  border-radius: 0.45rem;
  padding: 0.55rem 0.7rem 0.6rem;
}
.chip-name {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  color: #1c1c1c;
}
.chip-sub {
  font-size: 0.98rem;
  line-height: 1.32;
  color: #33343a;
  margin-top: 0.1rem;
}
.arrow {
  align-self: center;
  color: var(--color-primary);
  font-size: 1.3rem;
  line-height: 1;
}

/* The badge is the point of the slide: every box is already in the demo, and every
   one of them is in it further than the room was told and less far than production. */
.badge {
  margin-top: auto;
  padding-top: 0.5rem;
  font-family: var(--font-code);
  font-size: 0.85rem;
  letter-spacing: 0.04em;
  color: #5f6066;
}
.badge.on::before {
  content: '\2714\00a0\00a0';
  color: #3f8a46;
  font-weight: 700;
}
</style>
