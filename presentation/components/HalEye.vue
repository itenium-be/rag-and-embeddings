<!-- Pure-CSS glowing red machine eye — scans, breathes, flickers -->
<template>
  <div class="hal-eye">
    <div class="hal-eye__sweep" />
    <div class="hal-eye__pupil" />
  </div>
</template>

<style scoped>
.hal-eye {
  position: relative;
  width: 130px;
  height: 130px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: radial-gradient(circle at 50% 45%, #25000a 0%, #140006 45%, #060608 72%);
  box-shadow: 0 0 45px rgba(255, 31, 61, .45), inset 0 0 35px #000;
  animation: hal-flicker 7s linear infinite;
}

/* rotating radar sweep glinting across the lens */
.hal-eye__sweep {
  position: absolute;
  inset: -25%;
  background: conic-gradient(from 0deg, transparent 0deg, rgba(255, 31, 61, .5) 32deg, transparent 64deg);
  animation: hal-sweep 4s linear infinite;
}

/* breathing core */
.hal-eye__pupil {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: radial-gradient(circle, #fff 0%, #ff1f3d 38%, #b3001b 72%);
  box-shadow: 0 0 25px #ff1f3d, 0 0 55px rgba(255, 31, 61, .7);
  animation: hal-pulse 3.2s ease-in-out infinite;
}

@keyframes hal-sweep {
  to { transform: rotate(360deg); }
}
@keyframes hal-pulse {
  0%, 100% { box-shadow: 0 0 22px #ff1f3d, 0 0 45px rgba(255, 31, 61, .55); transform: scale(1); }
  50%      { box-shadow: 0 0 34px #ff1f3d, 0 0 80px rgba(255, 31, 61, .9);  transform: scale(1.08); }
}
@keyframes hal-flicker {
  0%, 92%, 100% { opacity: 1; }
  93% { opacity: .68; }
  95% { opacity: 1; }
  96% { opacity: .82; }
  97% { opacity: 1; }
}
</style>
