<template>
  <div class="qp">

    <div class="qbar reveal" :class="{ shown: clicks >= 1 }">
      Wie kan me helpen met Kubernetes?
    </div>

    <div class="stem-only reveal" :class="{ shown: clicks >= 2 }">
      <span class="rule"></span>
      <span class="chev"></span>
    </div>

    <div class="agent reveal" :class="{ shown: clicks >= 2 }">
      <span class="llm"><StochasticParrot /></span>
      retriever agent
      <em>a system prompt selects one or more retrievers</em>
    </div>

    <div class="fan">
      <span class="rule stem reveal" :class="{ shown: clicks >= 3 }"></span>
      <span class="rail reveal" :class="{ shown: clicks >= 3 }"></span>
      <template v-for="(c, i) in COLS" :key="c">
        <span class="rule leg reveal" :class="{ shown: clicks >= 3 + i }" :style="{ left: c }"></span>
        <span class="chev reveal" :class="{ shown: clicks >= 3 + i }" :style="{ left: c }"></span>
      </template>
    </div>

    <div class="sources">
      <div
        v-for="s in sources" :key="s.name"
        class="src reveal" :class="[s.kind, { shown: clicks >= s.at }]"
      >
        <span class="sname">{{ s.name }}</span>
        <em>{{ s.what }}</em>
        <b>{{ s.tag }}</b>
      </div>
    </div>

    <div class="fan up reveal" :class="{ shown: clicks >= 6 }">
      <span v-for="c in COLS" :key="c" class="rule leg" :style="{ left: c }"></span>
      <span class="rail"></span>
      <span class="rule stem"></span>
      <span class="chev mid"></span>
    </div>

    <div class="prompt reveal" :class="{ shown: clicks >= 6 }">
      stuffed into the prompt
      <em>the model only ever sees what retrieval handed it</em>
    </div>

    <div class="tail reveal" :class="{ shown: clicks >= 7 }">
      <span class="answer-model">
        <span class="llm"><StochasticParrot /></span>
        answer model
        <span class="rule into"></span>
        <span class="chev into"></span>
      </span>
      <span class="arr">&rarr;</span>
      <span class="answer">answer + citations</span>
    </div>

    <div class="sources left-out reveal" :class="{ shown: clicks >= 8 }">
      <div v-for="s in leftOut" :key="s.name" class="src off">
        <span v-if="s.llm" class="llm"><StochasticParrot /></span>
        <span class="sname">{{ s.name }}</span>
        <em>{{ s.what }}</em>
        <b>not today</b>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })

// Column centres of the three-source grid. A third of the width is not the centre once
// the gap is taken out, so the outer two are derived from the real column width.
const EDGE = 'calc((100% - 2 * var(--gap)) / 6)'
const COLS = [EDGE, '50%', `calc(100% - ${EDGE})`]

// Only the first is wired up in the demo. The other two are what retrieval turns into
// once the answer is not sitting in a passage anywhere — named, not built.
const sources = [
  { name: 'vector search', what: 'nearest chunks by cosine', tag: 'this demo', kind: 'ours', at: 3 },
  { name: 'API call', what: 'deterministic code that calls BambooHR', tag: 'not today', kind: 'off', at: 4 },
  { name: 'SQL query', what: 'prepared queries — or text-to-SQL', tag: 'not today', kind: 'off', at: 5 },
]

// Not retrievers - the three things wrapped around the whole pipeline that this session
// never gets to.
const leftOut = [
  { name: 'access control', what: 'who asks decides which chunks exist' },
  { name: 'answer critic loop', what: 'the model judges its own answer and retries', llm: true },
  { name: 'evaluation', what: 'proving a change made retrieval better' },
]
</script>

<style scoped>
.qp {
  --gap: 1.4rem;
  /* Every chevron centre stops this far short of the box it points into — the same
     clearance the arrows on the pipeline slide leave. */
  --clearance: 8px;
  --tail-stem: 0.8rem;
  display: flex;
  flex-direction: column;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.qbar {
  border-left: 4px solid var(--color-primary);
  border-radius: 0 0.4rem 0.4rem 0;
  background: #ffe2d2;
  padding: 0.5rem 0.9rem;
  font-size: 1.15rem;
  color: #8a2f00;
}

/* Every connector is built from the same two pieces: a 2px rule and an open chevron,
   never a filled head. */
.rule {
  position: absolute;
  width: 2px;
  background: var(--color-primary);
}
.chev {
  position: absolute;
  width: 10px;
  height: 10px;
  box-sizing: border-box;
  border-right: 2px solid var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  transform: translate(-50%, -50%) rotate(45deg);
}

.stem-only {
  position: relative;
  height: 1.25rem;
}
.stem-only .rule {
  left: 50%;
  top: 0;
  bottom: var(--clearance);
  margin-left: -1px;
}
.stem-only .chev {
  left: 50%;
  top: calc(100% - var(--clearance));
}

.agent,
.prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid var(--color-primary);
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.4rem 0.8rem 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1c1c1c;
}
.agent { position: relative; }
.agent em,
.prompt em {
  font-style: normal;
  font-size: 0.78rem;
  font-weight: 400;
  margin-top: 0.15rem;
  color: #5f6066;
}

/* The parrot marks the boxes that are a call to a language model, and only those: the
   embedding model and the cross-encoder are neural too, and neither is one. It hangs off
   the corner rather than sitting inside, so adding one never resizes a box — the fan legs
   and chevrons are pinned to box centres. The disc carries the box's own border so the
   badge reads as part of the box it sits on rather than pasted over it. */
.llm {
  position: absolute;
  top: -0.85rem;
  right: -0.85rem;
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  box-sizing: border-box;
  border: 2px solid var(--color-primary);
  border-radius: 50%;
  background: #fefefe;
}
/* The left-out row sits directly under the answer box, and the slide has no vertical room
   left to push it further down, so this disc rides lower on its corner than the others. */
.src.off .llm {
  top: -0.45rem;
  border-color: #a8a8a8;
  border-style: dashed;
}
.llm :deep(svg) { width: 1.35rem; height: auto; }

.fan {
  position: relative;
  height: 2.2rem;
}
.fan .stem {
  left: 50%;
  top: 0;
  height: 1.05rem;
  margin-left: -1px;
}
.fan .rail {
  position: absolute;
  top: 1.05rem;
  left: calc((100% - 2 * var(--gap)) / 6);
  right: calc((100% - 2 * var(--gap)) / 6);
  height: 2px;
  background: var(--color-primary);
}
.fan .leg {
  top: 1.05rem;
  bottom: var(--clearance);
  margin-left: -1px;
}
.fan > .chev {
  top: calc(100% - var(--clearance));
}

/* The converging fan is the same shape upside down: legs first, then the rail, then one
   stem into the prompt. */
.fan.up .leg {
  top: 0;
  bottom: 1.25rem;
}
.fan.up .rail {
  top: auto;
  bottom: 1.25rem;
}
.fan.up .stem {
  top: auto;
  bottom: var(--clearance);
  height: calc(1.25rem - var(--clearance));
}
.fan.up .chev.mid {
  left: 50%;
  top: calc(100% - var(--clearance));
}

.sources {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap);
}
.src {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px solid #a8a8a8;
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.4rem 0.6rem 0.5rem;
  text-align: center;
}
.src.ours { border-color: #3f8a46; background: #edf6ee; }
.src.off { border-style: dashed; }
.sname {
  font-size: 1.05rem;
  font-weight: 700;
  color: #1c1c1c;
}
.src em {
  font-style: normal;
  font-size: 0.78rem;
  line-height: 1.25;
  margin-top: 0.15rem;
  color: #5f6066;
}
.src b {
  font-family: var(--font-code);
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-top: 0.4rem;
  padding: 0.1rem 0.4rem 0.15rem;
  border-radius: 0.25rem;
  background: #e4e4e4;
  color: #5f6066;
}
.src.ours b { background: #276b2e; color: #fefefe; }

.tail {
  margin-top: var(--tail-stem);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}
/* The arrow into the answer model hangs off that box, not off the slide centre: the
   tail is a centred row of two boxes, so 50% of the row falls between them. */
.answer-model { position: relative; }
.answer-model .rule.into {
  left: 50%;
  margin-left: -1px;
  top: calc(-1 * var(--tail-stem) - 2px);
  height: calc(var(--tail-stem) + 2px - var(--clearance));
}
.answer-model .chev.into {
  left: 50%;
  top: calc(-1 * var(--clearance) - 2px);
}

.answer-model,
.answer {
  border: 2px solid var(--color-primary);
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.45rem 1.1rem 0.5rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: #1c1c1c;
}
/* Room on the right for the parrot: on a box this narrow the disc otherwise sits over
   the word rather than over the corner. */
.answer-model { padding-right: 2.2rem; }
.answer {
  border-color: #3f8a46;
  background: #edf6ee;
}
.arr {
  font-size: 1.4rem;
  line-height: 1;
  color: var(--color-primary);
}

/* Nothing points into these: they are not retrievers the fan could have chosen, so they
   sit detached below the answer. The gap also clears the critic loop's parrot, which
   hangs above its box and would otherwise touch the answer box. */
.left-out { margin-top: 0.6rem; }
</style>
