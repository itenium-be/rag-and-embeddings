<template>
  <div class="contrast">

    <div class="row">
      <div class="row-tag closed">closed book</div>
      <div class="card question">&ldquo;When does the<br>bakery close?&rdquo;</div>
      <div class="arrow">&rarr;</div>
      <div class="stage-slot spacer"></div>
      <div class="arrow spacer-arrow">&rarr;</div>
      <div class="bird"><StochasticParrot /></div>
      <div class="arrow">&rarr;</div>
      <div class="card answer wrong" :class="{ shown: clicks >= 1 }">
        &ldquo;Probably 17:00.&rdquo;
        <span class="verdict">confident. invented.</span>
      </div>
    </div>

    <div class="divider"></div>

    <div class="row second" :class="{ shown: clicks >= 2 }">
      <div class="row-tag open">open book</div>
      <div class="card question">&ldquo;When does the<br>bakery close?&rdquo;</div>
      <div class="arrow">&rarr;</div>
      <div class="stage-slot">
        <div class="docs">
          <span class="doc d3"></span>
          <span class="doc d2"></span>
          <span class="doc d1"></span>
        </div>
        <div class="stage-name"><b>R</b>etrieval + <b>A</b>ugmented</div>
        <div class="stage-desc">find the page, staple it on</div>
      </div>
      <div class="arrow">&rarr;</div>
      <div class="bird"><StochasticParrot /></div>
      <div class="arrow">&rarr;</div>
      <div class="card answer right" :class="{ shown: clicks >= 3 }">
        &ldquo;18:00, closed Sunday.&rdquo;
        <span class="verdict">same parrot. it can read.</span>
      </div>
    </div>

  </div>
</template>

<script setup>
defineProps({ clicks: { type: Number, default: 0 } })
</script>

<style scoped>
.contrast {
  margin: 2.6rem -2.5rem 0 -6rem;
}

.row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
}
.row.second {
  opacity: 0;
  transform: translateY(0.6rem);
  transition: opacity 420ms ease, transform 420ms ease;
}
.row.second.shown {
  opacity: 1;
  transform: none;
}

.divider {
  height: 2px;
  background: #e6e6e6;
  margin: 2.9rem 3rem;
}

.row-tag {
  flex: 0 0 7rem;
  font-family: var(--font-code);
  font-size: 0.95rem;
  font-weight: 500;
  text-align: right;
  padding-right: 0.4rem;
}
.row-tag.closed { color: #8a8a8a; }
.row-tag.open { color: var(--color-primary); }

.arrow {
  flex: 0 0 auto;
  font-size: 1.9rem;
  line-height: 1;
  color: #b6b6b6;
}
.row.second .arrow { color: var(--color-primary); }

.card {
  flex: 0 0 10.2rem;
  border-radius: 0.6rem;
  padding: 0.9rem 0.7rem;
  font-size: 0.92rem;
  line-height: 1.45;
  text-align: center;
  color: #232323;
}
.card.question {
  border: 2px solid #d8d8d8;
  background: white;
}
.card.answer {
  flex: 0 0 11.2rem;
  opacity: 0;
  transition: opacity 380ms ease;
}
.card.answer.shown { opacity: 1; }
.card.answer.wrong {
  border: 2px solid #d98b82;
  background: #fdf1ef;
}
.card.answer.right {
  border: 2px solid #7ba97e;
  background: #f0f7f0;
}
.verdict {
  display: block;
  margin-top: 0.45rem;
  font-family: var(--font-code);
  font-size: 0.72rem;
  letter-spacing: 0.02em;
}
.wrong .verdict { color: #b23c2c; }
.right .verdict { color: #2f6d35; }

.stage-slot {
  flex: 0 0 10.6rem;
  text-align: center;
}
.stage-slot.spacer { visibility: hidden; }
.spacer-arrow { visibility: hidden; }

.docs {
  position: relative;
  height: 3.2rem;
  margin-bottom: 0.45rem;
}
.doc {
  position: absolute;
  left: 50%;
  top: 0;
  width: 2.1rem;
  height: 2.9rem;
  border: 2px solid var(--color-primary);
  border-radius: 0.2rem;
  background: white;
}
.d1 { transform: translateX(-50%); }
.d2 { transform: translateX(-50%) translate(-0.95rem, 0.22rem) rotate(-7deg); opacity: 0.75; }
.d3 { transform: translateX(-50%) translate(0.95rem, 0.22rem) rotate(7deg); opacity: 0.75; }

.stage-name {
  font-family: var(--font-heading);
  font-size: 1rem;
  color: #232323;
}
.stage-name b { color: var(--color-primary); }
.stage-desc {
  font-size: 0.78rem;
  line-height: 1.4;
  margin-top: 0.3rem;
  color: #5b5c62;
}

.bird {
  flex: 0 0 5rem;
}
.bird :deep(.parrot) {
  width: 4.8rem;
  height: auto;
  margin: 0 auto;
}
</style>
