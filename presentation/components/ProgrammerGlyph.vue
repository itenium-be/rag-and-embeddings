<template>
  <svg class="programmer" viewBox="0 0 120 128" role="img" aria-label="programmer">
    <path class="torso" d="M30 112 C 30 86, 43 76, 60 76 C 77 76, 90 86, 90 112 Z" />
    <circle class="head" cx="60" cy="47" r="20" />
    <path class="hair" d="M39 46 C 39 28, 50 21, 60 21 C 70 21, 81 28, 81 46 C 76 37, 69 33, 60 33 C 51 33, 44 37, 39 46 Z" />
    <rect class="lens" x="45" y="43" width="13" height="11" rx="3" />
    <rect class="lens" x="62" y="43" width="13" height="11" rx="3" />
    <path class="bridge" d="M58 48 L62 48" />
    <rect class="screen" x="33" y="84" width="54" height="24" rx="2.5" />
    <path class="laptop" d="M19 108 L101 108 L95 118 L25 118 Z" />
    <path class="code" d="M40 91 L52 91 M40 97 L62 97 M40 103 L48 103" />
    <rect class="desk" x="22" y="111" width="76" height="5" rx="2.5" />
  </svg>
</template>

<style scoped>
.programmer { display: block; }
.torso { fill: var(--color-primary); }
.head { fill: #f1b06c; }
.hair { fill: #343434; }
.lens { fill: #fefefe; stroke: #343434; stroke-width: 2.5; }
.bridge { stroke: #343434; stroke-width: 2.5; }
.screen { fill: #343434; }
.laptop { fill: #b83800; }
.code { stroke: #8d8d8d; stroke-width: 2.5; stroke-linecap: round; }
.desk { fill: #b9b9b9; }
</style>
