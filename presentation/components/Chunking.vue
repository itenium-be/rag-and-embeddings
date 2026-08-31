<template>
  <div class="chunking">

    <div class="left">
      <div class="side reveal" :class="{ shown: clicks >= 1 }">
        <div class="doc">
          <span v-for="n in 8" :key="n" class="rule" :class="{ short: n % 4 === 0 }"></span>
        </div>
        <div class="name">Arbeidsreglement.pdf</div>
        <div class="counts">
          <span class="count">37 pages</span>
          <span class="count">92k chars</span>
        </div>
      </div>

      <span class="arrow reveal" :class="{ shown: clicks >= 2 }">&darr;</span>

      <div class="side reveal" :class="{ shown: clicks >= 2 }">
        <div class="deck">
          <span v-for="n in 5" :key="n" class="card" :style="cardStyle(n)"></span>
        </div>
        <div class="name">index cards</div>
        <div class="counts">
          <span class="count">133 chunks</span>
        </div>
      </div>
    </div>

    <div class="right">
      <div
        v-for="group in groups"
        :key="group.head"
        class="group reveal"
        :class="{ shown: clicks >= group.at }"
      >
        <div class="ghead">
          <span>{{ group.head }}</span>
          <span>{{ group.sub }}</span>
        </div>
        <div v-for="r in group.rows" :key="r.key" class="trow">
          <span class="tkey">
            {{ r.key }}
            <b v-if="r.ours" class="ours">{{ r.ours }}</b>
          </span>
          <span class="tval">{{ r.val }}</span>
        </div>
      </div>

      <div class="note reveal" :class="{ shown: clicks >= 4 }">
        Claude cut on <code>¶</code> &rarr; <code>line</code> &rarr; <code>sentence</code>
        &rarr; <code>word</code>. Chunk at max 800 chars.
      </div>
    </div>

    <span class="link reveal" :class="{ shown: clicks >= 4 }">
      <span class="link-line"></span>
      <span class="link-head"></span>
    </span>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// `ours` marks what app/rag/chunking.py actually does: split_text(size=800, overlap=100).
const groups = [
  {
    head: 'CUT ON', sub: 'TRADE-OFF', at: 3,
    rows: [
      { key: 'paragraph / section', val: 'follows the author, sizes vary wildly' },
      { key: 'fixed characters', ours: '800', val: 'predictable, cuts mid-sentence' },
      { key: 'fixed tokens', val: "matches the model's limit, needs its tokenizer" },
    ],
  },
  {
    head: 'THEN ADD', sub: 'BUYS YOU', at: 4,
    rows: [
      { key: 'overlap', ours: '100', val: 'the cut sentence survives, stored twice' },
      { key: 'parent link', val: 'retrieve the card, send the section around it' },
      { key: 'metadata', val: 'source, person, date — filter before ranking' },
    ],
  },
]

// Fanned by hand. Five cards is enough to read as a stack without the angles
// turning into a mess.
const angles = [-7, -3.5, 0, 3.5, 7]
const cardStyle = (n) => ({
  transform: `rotate(${angles[n - 1]}deg) translateY(${Math.abs(angles[n - 1]) * 0.35}px)`,
  zIndex: String(n === 3 ? 5 : 3 - Math.abs(n - 3)),
})
</script>

<style scoped>
.chunking {
  position: relative;
  display: grid;
  grid-template-columns: 18rem 1fr;
  gap: 1.6rem;
  margin-top: 0.9rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.left {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.side {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.doc {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.5rem;
  width: 7.2rem;
  height: 8.6rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
  padding: 0 0.9rem;
}
.rule {
  height: 0.32rem;
  border-radius: 0.2rem;
  background: #d5d5d5;
}
.rule.short { width: 55%; }

.deck {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 7.2rem;
  height: 6.4rem;
}
.card {
  position: absolute;
  width: 6.4rem;
  height: 4.2rem;
  border: 2px solid #a8a8a8;
  border-radius: 0.4rem;
  background: #fefefe;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.07);
}

.name {
  font-size: 1rem;
  margin-top: 0.65rem;
  color: #1c1c1c;
}
.counts {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.35rem;
}
.count {
  font-family: var(--font-code);
  font-size: 0.9rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem 0.25rem;
  border-radius: 0.35rem;
  background: #343434;
  color: #fefefe;
}

.arrow {
  font-size: 1.9rem;
  line-height: 1;
  margin: 0.5rem 0;
  color: var(--color-primary);
}

.group { margin-bottom: 0.9rem; }
.group + .group { margin-top: 2.4rem; }

.ghead {
  display: flex;
  gap: 1rem;
  padding-bottom: 0.35rem;
  border-bottom: 2px solid #a8a8a8;
}
.ghead span {
  font-family: var(--font-code);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  color: #5f6066;
}
.ghead span:first-child { flex: 0 0 11.5rem; }

.trow {
  display: flex;
  gap: 1rem;
  align-items: baseline;
  padding: 0.65rem 0;
  border-bottom: 1px solid #d5d5d5;
}
.tkey {
  flex: 0 0 11.5rem;
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.95rem;
  color: #1c1c1c;
}
.ours {
  font-family: var(--font-code);
  font-size: 0.72rem;
  font-weight: 700;
  padding: 0.1rem 0.35rem 0.15rem;
  border-radius: 0.25rem;
  background: #ffe2d2;
  color: #8a2f00;
}
.tval {
  flex: 1;
  font-size: 0.9rem;
  line-height: 1.25;
  color: #33343a;
}

.note {
  margin-top: 2.4rem;
  font-size: 0.88rem;
  color: #5f6066;
}
.note code {
  font-family: var(--font-code);
  font-size: 0.85rem;
  color: #fefefe;
}

/* Spans the grid gutter from the chunk count to the note, so the two columns read as
   one sentence rather than as unrelated panels. */
.link {
  position: absolute;
  left: 12.8rem;
  bottom: 0.85rem;
  width: 6.2rem;
  height: 0;
}
.link-line {
  position: absolute;
  left: 0;
  right: 0;
  top: -1px;
  height: 2px;
  background: var(--color-primary);
}
.link-head {
  position: absolute;
  right: 0;
  top: -0.3rem;
  width: 0.6rem;
  height: 0.6rem;
  border-top: 2px solid var(--color-primary);
  border-right: 2px solid var(--color-primary);
  transform: rotate(45deg);
}
</style>
