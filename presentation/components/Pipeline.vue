<template>
  <div class="pipeline">

    <div class="phase reveal" :class="{ shown: clicks >= 1 }">
      Ingestion <span class="when">once, up front</span>
    </div>

    <div class="row">
      <div class="slot reveal" :class="{ shown: clicks >= 1 }">
        <div class="box">documents</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 1 }">
        <span class="arrow">&rarr;</span>
        <div class="box">chunks</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 1 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">embedding<br>model<em>e5-small · 384 dims</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 1 }">
        <span class="arrow">&rarr;</span>
        <div class="box store">store<em>chunks.jsonl<br>embeddings.npy</em></div>
        <span class="elbow reveal" :class="{ shown: clicks >= 3 }"><span class="head"></span></span>
      </div>
      <div class="slot"></div>
    </div>

    <div class="phase second reveal" :class="{ shown: clicks >= 2 }">
      Query <span class="when">every question</span>
    </div>

    <div class="row">
      <div class="slot reveal" :class="{ shown: clicks >= 2 }">
        <div class="box">question</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 2 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">embedding<br>model<em>e5-small · 384 dims</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 2 }">
        <span class="arrow">&rarr;</span>
        <div class="box target">nearest<br>chunks</div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 4 }">
        <span class="arrow">&rarr;</span>
        <div class="box model">answer<br>model<em>claude-opus-5</em></div>
      </div>
      <div class="slot reveal" :class="{ shown: clicks >= 4 }">
        <span class="arrow">&rarr;</span>
        <div class="box answer">answer</div>
      </div>
    </div>

    <div class="note reveal" :class="{ shown: clicks >= 5 }">
      Two different models: one turns text into coordinates, one writes the answer
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
  height: 5.4rem;
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
  line-height: 1.35;
  letter-spacing: 0.01em;
  margin-top: 0.35rem;
  color: #5f6066;
}
.box.store em { color: #b9b9b9; }

.box.store {
  background: #343434;
  border-color: #343434;
  color: #fefefe;
}
.box.answer {
  border-color: #3f8a46;
  background: #edf6ee;
  color: #1c1c1c;
}

/* Down out of the store, one slot to the left, down again into the chunks it
   answers with. Slots are equal-width flex children, so one slot is exactly the
   pitch between two box centres; the inset is half a box, which puts the legs on
   the box centres rather than the slot centres. */
.elbow {
  position: absolute;
  right: 4.28rem;
  top: 100%;
  box-sizing: border-box;
  width: 100%;
  height: 5.2rem;
  border: 2px solid var(--color-primary);
  border-top: 0;
}
/* Open chevron, never a filled head — same as every arrow in the deck. */
.elbow .head {
  position: absolute;
  left: -2px;
  top: 100%;
  width: 10px;
  height: 10px;
  box-sizing: border-box;
  border-right: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  transform: translate(-50%, -50%) rotate(45deg);
}

.note {
  padding-top: 2.4rem;
  font-size: 1.1rem;
  text-align: center;
  color: #33343a;
}
</style>
