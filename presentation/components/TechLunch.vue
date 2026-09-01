<template>
  <div class="tech-lunch">

    <div class="badges">
      <span class="badge">Office Day</span>
      <span class="badge badge--outline">Lightning Talks</span>
    </div>

    <div class="prompts">
      <div v-for="p in prompts" :key="p" class="prompt">
        <span class="mark">&rsaquo;</span>{{ p }}
      </div>
    </div>

    <div class="lunch">
      <span class="emoji">&#129386;</span>
      <span class="lunch-text">Broodjes voorzien</span>
    </div>

  </div>
</template>

<script setup>
const prompts = [
  'Iets nieuws ontdekt?',
  'Een tool of aanpak die werkt?',
  'Een case, experiment of inzicht?',
  'Of net een vraag voor de anderen?',
]
</script>

<style scoped>
.tech-lunch {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
  /* rem throughout: the layout's textSize class sets a font-size on the column, and
     em-based sizing here would scale twice. */
  font-size: 1rem;
}

.badges {
  display: flex;
  gap: 0.5rem;
}
.badge {
  font-family: var(--font-code);
  font-size: 0.78rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 0.4em 0.9em;
  border-radius: 999px;
  border: 2px solid var(--color-primary);
  background: var(--color-primary);
  color: #fefefe;
  white-space: nowrap;
}
.badge--outline {
  background: transparent;
  color: var(--color-primary);
}

.prompts {
  border: 2px solid #a8a8a8;
  border-radius: 0.6rem;
  background: #fefefe;
  padding: 0.35rem 1.1rem;
}
.prompt {
  display: flex;
  align-items: baseline;
  gap: 0.7rem;
  padding: 0.62rem 0;
  font-size: 1.12rem;
  line-height: 1.3;
  color: #33343a;
  border-top: 1px solid #e2e2e2;
}
.prompt:first-child { border-top: 0; }
.mark {
  flex: 0 0 auto;
  font-size: 1.5rem;
  line-height: 0.9;
  font-weight: 700;
  color: var(--color-primary);
}

.lunch {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  border-left: 5px solid var(--color-primary);
  border-radius: 0 0.5rem 0.5rem 0;
  background: #ffe2d2;
  padding: 0.7rem 1.1rem;
}
.emoji {
  font-size: 1.5rem;
  line-height: 1;
}
.lunch-text {
  font-family: var(--font-heading);
  font-size: 1.2rem;
  font-weight: 700;
  color: #8a2f00;
}
</style>
