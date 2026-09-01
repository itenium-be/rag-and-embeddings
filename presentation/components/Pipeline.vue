<template>
  <div class="pipeline">

    <div class="phase reveal" :class="{ shown: clicks >= 1 }">
      Ingestion <span class="when">once, up front</span>
    </div>

    <div class="row">
      <div class="slot reveal" :class="{ shown: clicks >= 1 }">
        <div class="box">documents<em>pdf, xlsx, docx</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 2 }">
        <span class="arrow">&rarr;</span>
        <div class="box">chunks<em>max 800<span class="sep">&middot;</span>100 overlap</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 3 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">embedding<br>model<em>e5-small<span class="sep">&middot;</span>384 dims</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 4 }">
        <span class="arrow">&rarr;</span>
        <div class="box store">store<em>chunks.jsonl<br>embeddings.npy</em></div>
        <span class="elbow reveal" :class="{ shown: clicks >= 7 }">
          <span class="leg down"></span>
          <span class="bar"></span>
          <span class="leg into"></span>
          <span class="head"></span>
        </span>
      </div>
      <div class="slot"></div>
    </div>

    <div class="phase second reveal" :class="{ shown: clicks >= 5 }">
      Query <span class="when">every question</span>
    </div>

    <div class="row">
      <div class="slot reveal" :class="{ shown: clicks >= 5 }">
        <div class="box">question</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 6 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">embedding<br>model<em>e5-small<span class="sep">&middot;</span>384 dims</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 7 }">
        <span class="arrow">&rarr;</span>
        <div class="box target">search<em>cosine, then sort</em></div>
        <div class="bubble reveal" :class="{ shown: clicks === 7 }">
          Every question is compared against <b>all</b> chunks. Fine at 2194 &mdash; when
          that number explodes you index instead of scan, in a vector database like
          <b>Elasticsearch</b>.
        </div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 8 }">
        <span class="arrow">&rarr;</span>
        <div class="box">nearest chunks<br>+ question</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 9 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">answer<br>model<em>claude-opus-5</em></div>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.pipeline { margin-top: 1.2rem; }

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.phase {
  font-family: var(--font-heading);
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding-bottom: 0.5rem;
  color: #1c1c1c;
}
.phase.second { padding-top: 5.2rem; }
.when {
  font-family: var(--font-code);
  font-size: 0.85rem;
  font-weight: 400;
  letter-spacing: 0.03em;
  padding-left: 0.5rem;
  color: #5f6066;
}

/* Five equal slots in both rows, so the store lands one slot right of the chunks it
   feeds and the elbow between the rows is the only thing that has to bend. */
.row {
  display: flex;
  align-items: stretch;
}
.slot {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.slot .arrow {
  flex: 0 0 auto;
  font-size: 1.5rem;
  line-height: 1;
  color: var(--color-primary);
}

.box {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 5.7rem;
  box-sizing: border-box;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.4rem 0.5rem;
  font-size: 1.05rem;
  line-height: 1.25;
  text-align: center;
  color: #33343a;
}
.box.model {
  border-color: var(--color-primary);
  font-weight: 700;
  color: #1c1c1c;
}

/* Names the concrete thing in the box: the two boxes that say "model" are two different
   models, and the store is a pair of files rather than a database. */
.box em {
  font-family: var(--font-code);
  font-style: normal;
  font-size: 0.62rem;
  font-weight: 400;
  line-height: 1.1;
  letter-spacing: 0.01em;
  margin-top: 0.25rem;
  color: #5f6066;
}
/* The separator sits on a line of its own between the two values; a collapsed
   line-height keeps that from costing a full extra line. The dot's ink sits high in its
   own line box, so it needs nudging down to look centred between the two lines. */
.box em .sep {
  display: block;
  position: relative;
  top: 1.5px;
  line-height: 0.75;
}
.box.store em { color: #b9b9b9; }

.box.store {
  background: #343434;
  border-color: #343434;
  color: #fefefe;
}

/* Anchored to the box rather than the slot: the arrow to its left takes 2rem out of
   the slot, so the slot centre is not the box centre. */
.bubble {
  position: absolute;
  top: calc(100% + 0.6rem);
  left: calc(50% + 1rem);
  transform: translateX(-50%);
  width: 30rem;
  box-sizing: border-box;
  border: 2px solid var(--color-primary);
  border-radius: 0.6rem;
  background: #fffdf7;
  padding: 0.7rem 0.9rem;
  font-size: 0.86rem;
  line-height: 1.35;
  text-align: center;
  color: #33343a;
}
/* Tail: a rotated square that covers the border it pokes through. */
.bubble::before {
  content: '';
  position: absolute;
  left: 50%;
  top: -7px;
  width: 12px;
  height: 12px;
  background: #fffdf7;
  border-left: 2px solid var(--color-primary);
  border-top: 2px solid var(--color-primary);
  transform: translateX(-50%) rotate(45deg);
}

/* Down out of the store, one slot to the left, down again into the chunks it answers
   with. Slots are equal-width flex children, so one slot is exactly the pitch between
   two box centres; the inset is half a box, which puts the legs on the box centres
   rather than the slot centres. The height stops the chevron 8px short of the target
   box, the same clearance the horizontal arrows leave. */
.elbow {
  position: absolute;
  right: 4.28rem;
  top: 100%;
  width: 100%;
  height: 6.484rem;
}
.elbow .leg {
  position: absolute;
  width: 2px;
  background: var(--color-primary);
}
/* The two legs are deliberately unequal: short out of the store, long into the box it
   feeds, so the shape reads as a path rather than a bracket. */
.elbow .leg.down {
  right: 0;
  margin-right: -1px;
  top: 0;
  height: 3.8rem;
}
.elbow .leg.into {
  left: 0;
  margin-left: -1px;
  top: 3.8rem;
  bottom: 0;
}
.elbow .bar {
  position: absolute;
  left: 0;
  right: 0;
  top: 3.8rem;
  height: 2px;
  background: var(--color-primary);
}
/* Open chevron, never a filled head — same as every arrow in the deck. */
.elbow .head {
  position: absolute;
  left: 0;
  top: 100%;
  width: 10px;
  height: 10px;
  box-sizing: border-box;
  border-right: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  transform: translate(-50%, -50%) rotate(45deg);
}

</style>
