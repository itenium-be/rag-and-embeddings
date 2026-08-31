<template>
  <svg class="parrot" viewBox="0 0 120 128" role="img" aria-label="parrot">
    <path class="tail" d="M64 92 C 74 108, 88 120, 106 127 C 94 111, 84 98, 78 86 Z" />
    <ellipse class="body" cx="56" cy="70" rx="26" ry="31" />
    <ellipse class="wing" cx="63" cy="69" rx="14" ry="23" />
    <path class="crest" d="M39 13 C 43 3, 54 1, 61 5 C 52 7, 45 11, 41 17 Z" />
    <circle class="head" cx="44" cy="33" r="21" />
    <path class="beak" d="M25 28 C 13 31, 9 42, 18 48 C 23 43, 26 38, 26 32 Z" />
    <circle class="eye" cx="38" cy="29" r="3.4" />
    <path class="legs" d="M50 100 L50 111 M62 100 L62 111" />
    <rect class="perch" x="22" y="111" width="76" height="5" rx="2.5" />
  </svg>
</template>

<style scoped>
.parrot { display: block; }
.body, .head, .crest { fill: var(--color-primary); }
.wing, .tail { fill: #b83800; }
.beak { fill: #343434; }
.eye { fill: #fefefe; }
.legs { stroke: #343434; stroke-width: 3.5; stroke-linecap: round; }
.perch { fill: #b9b9b9; }
</style>
