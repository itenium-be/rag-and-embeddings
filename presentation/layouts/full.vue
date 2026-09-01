<template>
  <div class="slidev-layout full">
    <slot />
  </div>
</template>

<style scoped>
/* Edge to edge and positioned, so a slide component can absolutely fill it. The
   itenium layouts all reserve padding for the footer and dot decorations; these
   guest slides bring their own chrome. */
.full {
  position: relative;
  overflow: hidden;
  height: 100%;
  padding: 0;
  background: #000;
}
</style>
