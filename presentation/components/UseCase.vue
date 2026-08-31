<template>
  <div class="use-case">

    <div class="sources">
      <div class="head">Sources</div>

      <div class="card reveal" :class="{ shown: clicks >= 1 }">
        <img class="logo" :src="sharepoint" alt="SharePoint">
        <div class="name">SharePoint</div>
        <div class="sub">20 policy PDFs</div>
      </div>

      <div class="card reveal" :class="{ shown: clicks >= 1 }">
        <img class="logo wordmark" :src="bamboohr" alt="BambooHR">
        <div class="name" aria-hidden="true">&nbsp;</div>
        <div class="sub">40 consultants &middot; credits ledger</div>
      </div>

      <div class="card reveal" :class="{ shown: clicks >= 1 }">
        <carbon-document-pdf class="logo glyph" />
        <div class="name">Consultant CVs</div>
        <div class="sub">40 PDFs</div>
      </div>
    </div>

    <div class="questions">
      <div class="head">Prompts</div>
      <div
        v-for="q in asked"
        :key="q"
        class="q reveal"
        :class="{ shown: clicks >= 2 }"
      >{{ q }}</div>
    </div>

  </div>
</template>

<script setup>
import sharepoint from '../images/sharepoint.svg'
import bamboohr from '../images/bamboohr.svg'

defineProps({ clicks: { type: Number, default: 0 } })

const asked = [
  'Welke AI tools mag ik gebruiken?',
  'Ik wil AZ-900 halen, wie heeft dat certificaat al?',
  'Wie kan me helpen met Kubernetes?',
  'Wat zijn de regels rond wagens en laptops?',
  'Hoeveel credits heeft Simon nog?',
]
</script>

<style scoped>
.use-case {
  display: flex;
  align-items: flex-start;
  gap: 2.6rem;
  margin-top: 1rem;
}

/* Nothing is ever dimmed: unrevealed items are fully transparent and keep their
   space, so the layout never shifts and nothing on screen looks washed out. */
.reveal {
  opacity: 0;
  transition: opacity 350ms ease;
}
.reveal.shown { opacity: 1; }

.head {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding-bottom: 0.6rem;
  color: #5f6066;
}

.sources { flex: 0 0 19rem; }
.questions { flex: 1; min-width: 0; }

.card {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  background: #fefefe;
  padding: 0.75rem 1rem 0.85rem;
  margin-bottom: 0.45rem;
  /* BambooHR's wordmark spells its own name, so that card's name line is an empty
     spacer: every card keeps the same structure and the subs line up on their own. */
  min-height: 7.2rem;
  box-sizing: border-box;
}

/* One height for every mark, so an icon and a wordmark carry the same weight in
   the row; the wordmark needs the wider cap to stay legible at that height. */
.logo {
  display: block;
  height: 1.8rem;
  width: auto;
  max-width: 6rem;
}
.logo.wordmark {
  height: 1.5rem;
  max-width: 11rem;
  margin: 0.15rem 0;
}
.logo.glyph {
  height: 1.8rem;
  width: 1.8rem;
  color: var(--color-primary);
}

.name {
  font-family: var(--font-heading);
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 0.35rem;
  color: #1c1c1c;
}
.sub {
  font-size: 0.95rem;
  margin-top: 0.15rem;
  color: #5f6066;
}


.q {
  border: 2px solid #a8a8a8;
  border-left: 5px solid var(--color-primary);
  border-radius: 0.5rem;
  background: #fefefe;
  padding: 0.8rem 1.1rem 0.9rem;
  margin-bottom: 1.25rem;
  font-size: 1.12rem;
  line-height: 1.35;
  color: #33343a;
}
</style>
