<template>
  <div class="demo-time reveal" :class="{ shown: clicks >= at }">
    <div class="badge">
      <span class="pop">🍿</span>
      <span class="txt">Demo Time</span>
      <span class="pop">🎬</span>
    </div>
    <div class="sub">enough slides &mdash; let's watch it live</div>
  </div>
</template>

<script setup>
defineProps({
  clicks: { type: Number, default: 0 },
  at: { type: Number, required: true },
})
</script>

<style scoped>
/* Anchored to `.content`, which is the layout's only positioned box, so left/right 0
   spans the full slide and the badge lands on the slide's centre line rather than the
   text column's. */
.demo-time {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 3.2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.55rem;
  pointer-events: none;
}

.reveal {
  opacity: 0;
  transition: opacity 250ms ease;
}
.reveal.shown { opacity: 1; }

.badge {
  display: flex;
  align-items: center;
  gap: 1.1rem;
  padding: 0.7rem 2.1rem 0.8rem;
  border-radius: 0.7rem;
  background: linear-gradient(100deg, #ff9d1f 0%, var(--color-primary) 45%, #ff5f1f 100%);
  box-shadow: 7px 7px 0 rgba(231, 130, 0, 0.22), 0 10px 30px rgba(0, 0, 0, 0.14);
  transform: rotate(-2.4deg);
}
.shown .badge {
  animation:
    pop 520ms cubic-bezier(0.2, 1.7, 0.4, 1) both,
    swagger 3.6s 700ms ease-in-out infinite;
}

.txt {
  font-family: var(--font-heading);
  font-size: 2.3rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  /* White text with a sheen sweeping through it, same trick as the sessions heading. */
  background: linear-gradient(100deg, #fff 0%, #fff 42%, #fff5d8 50%, #fff 58%, #fff 100%);
  background-size: 260% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  filter: drop-shadow(0 2px 1px rgba(120, 60, 0, 0.35));
  animation: sheen 3.2s linear infinite;
}
.pop {
  font-size: 1.9rem;
  line-height: 1;
  filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.2));
}
.shown .pop { animation: bounce 1.6s 900ms ease-in-out infinite; }

.sub {
  font-family: var(--font-code);
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: #5f6066;
}

@keyframes pop {
  0%   { transform: scale(0.35) rotate(11deg); }
  70%  { transform: scale(1.09) rotate(-4.5deg); }
  100% { transform: scale(1) rotate(-2.4deg); }
}
@keyframes swagger {
  0%, 100% { transform: rotate(-2.4deg) translateY(0); }
  50%      { transform: rotate(-1.2deg) translateY(-4px); }
}
@keyframes sheen { to { background-position: 260% center; } }
@keyframes bounce {
  0%, 100% { transform: translateY(0) rotate(0); }
  35%      { transform: translateY(-5px) rotate(-9deg); }
  70%      { transform: translateY(0) rotate(6deg); }
}

@media (prefers-reduced-motion: reduce) {
  .shown .badge,
  .shown .pop,
  .txt { animation: none; }
}
</style>
