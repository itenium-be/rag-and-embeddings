<script setup lang="ts">
// public/ assets are resolved through Vite's configured base so the deploy
// sub-path (--base /Extending-Your-Agent/) is honoured at build time.
const base = import.meta.env.BASE_URL
const hdr = `url(${base}hdr-alignment.jpg)`
const cover = `${base}the-alignment-problem.jpg`

// 10 squares per gauge; each gauge demos a different fill animation — pick the coolest.
const gauges = [
  { label: 'Brainpower',    filled: 10, anim: 'sweep'  },
  { label: 'Debate fuel',   filled: 10, anim: 'build'  },
  { label: 'Accessibility', filled: 6,  anim: 'charge' },
]
</script>

<template>
  <div class="dossier dx">
    <div class="wrap">
      <div class="bar"><span>// bookclub // next read</span><span class="g">CASE #03</span></div>
      <div class="dos">
        <div class="top" :style="{ '--hdr': hdr }">
          <div>
            <div class="case">AI / ETHICS · ACQUIRED 2020</div>
            <h1>The Alignment Problem</h1>
            <div class="auth">subject: Brian Christian</div>
          </div>
          <div class="id">PAGES <b>476</b></div>
        </div>
        <div class="grid">
          <div>
            <div class="quote">"How do we make machines want what we want?"</div>
            <div class="desc">The definitive narrative bridge from the basics of machine learning to the ethics of AI — the single best read spanning tech, philosophy and society at once.</div>
            <div class="for">
              <b>DATE POLL:</b> Second half of september
              <br><b>WHAT:</b> first chapter "PROPHECY" (100p)
            </div>
          </div>
          <div class="rcol">
            <div class="threat">
              <div class="t">// threat assessment</div>
              <div v-for="g in gauges" :key="g.label" class="gauge" :class="g.anim">
                <span>{{ g.label }}</span>
                <b>
                  <span v-for="n in 10" :key="n" class="sq"
                        :class="n <= g.filled ? 'on' : 'off'" :style="{ '--i': n - 1 }">█</span>
                </b>
              </div>
            </div>
            <figure class="vid"><img :src="cover" alt="cover"/></figure>
          </div>
        </div>
      </div>
      <div class="foot"><span>// itenium</span></div>
    </div>
  </div>
</template>

<style scoped>
.dossier{
  --bg:#04110a; --panel:#07180f; --grn:#27f08a; --dim:#1e7a4f;
  --ink:#bdf7d8; --amber:#ffb347; --line:#0f3b25;
  position:absolute;inset:0;
  background:
    radial-gradient(120% 90% at 50% 0%, #08361f 0%, var(--bg) 55%),
    var(--bg);
  color:var(--ink);
  font-family:'JetBrains Mono',monospace;
}
.dossier::after{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(0deg,rgba(0,0,0,.0) 0 2px,rgba(0,0,0,.28) 2px 3px);
  mix-blend-mode:multiply;opacity:.5;
}
.dx *{text-shadow:0 0 6px rgba(39,240,138,.18);}
.wrap{position:relative;height:100%;box-sizing:border-box;padding:2.2rem 2.8rem;display:flex;flex-direction:column;}
.bar{display:flex;justify-content:space-between;font-size:.72rem;letter-spacing:.16em;color:var(--dim);
  border-bottom:1px solid var(--line);padding-bottom:.5rem;text-transform:uppercase;}
.bar .g{color:var(--grn);}
.foot{position:absolute;left:2.8rem;right:2.8rem;bottom:1.4rem;display:flex;justify-content:space-between;
  font-size:.68rem;letter-spacing:.16em;color:var(--dim);text-transform:uppercase;}
.foot span:last-child{position:relative;top:8px;}

/* dossier */
.dos{flex:1;display:grid;grid-template-columns:1fr;gap:0;margin-top:.8rem;}
.dos .top{position:relative;display:grid;grid-template-columns:1fr auto;align-items:start;
  padding:.9rem 1.1rem .8rem;border:1px solid var(--line);border-radius:6px;overflow:hidden;
  background-image:linear-gradient(90deg, rgba(4,17,10,.95) 0 30%, rgba(4,17,10,.45) 60%, rgba(4,17,10,.18) 100%), var(--hdr, none);
  background-size:cover;background-position:center top;}
.dos .case{font-size:.74rem;letter-spacing:.2em;color:var(--dim);text-transform:uppercase;}
.dos h1{font-size:2.9rem;font-weight:800;color:var(--grn);margin:.4rem 0 .1rem;line-height:1;
  text-shadow:0 0 18px rgba(39,240,138,.4);}
.dos .auth{color:var(--ink);font-size:1.05rem;}
.dos .id{position:absolute;top:.6rem;right:1.1rem;z-index:4;text-align:right;font-size:.74rem;letter-spacing:.14em;color:var(--dim);text-transform:uppercase;line-height:1.6;text-shadow:0 0 6px rgba(0,0,0,.9);}
.dos .id b{color:var(--amber);}
.dos .grid{display:grid;grid-template-columns:1.35fr 1fr;gap:2rem;margin-top:1.1rem;}
.dos .quote{color:var(--amber);font-size:1.45rem;margin:.4rem 0 1.1rem;}
.dos .desc{font-size:1.02rem;line-height:1.5;color:var(--ink);}
.dos .threat{border:1px solid var(--line);border-radius:6px;padding:.85rem 1.2rem;background:var(--panel);}
.dos .rcol{display:flex;flex-direction:column;gap:1rem;align-self:start;}
.dos .vid{margin:0;align-self:flex-end;position:relative;width:132px;padding:.45rem;
  background:var(--panel);border:1px solid var(--line);border-radius:6px;box-shadow:0 0 18px rgba(39,240,138,.12);}
.dos .vid img{display:block;width:100%;border-radius:3px;
  filter:grayscale(.35) sepia(1) hue-rotate(70deg) saturate(2.2) brightness(.82) contrast(1.18);}
.dos .vid::after{content:"";position:absolute;inset:.45rem;border-radius:3px;
  pointer-events:none;background:repeating-linear-gradient(0deg,rgba(0,0,0,0) 0 2px,rgba(0,0,0,.32) 2px 3px);mix-blend-mode:multiply;}
.dos .threat .t{font-size:.72rem;letter-spacing:.18em;color:var(--dim);text-transform:uppercase;margin-bottom:.5rem;}
.dos .gauge{display:flex;justify-content:space-between;align-items:center;margin:.45rem 0;font-size:.82rem;
  letter-spacing:.08em;text-transform:uppercase;color:var(--dim);}
.dos .gauge b{display:inline-flex;gap:1px;font-size:.95rem;}
.dos .gauge .sq{display:inline-block;line-height:1;}
.dos .gauge .sq.on{color:var(--grn);}
.dos .gauge .sq.off{color:var(--line);}

/* three distinct fill styles — pick the coolest, then apply it to all three */
/* A · SWEEP — bar wipes in left→right as one motion */
.dos .gauge.sweep b{clip-path:inset(0 100% 0 0);animation:g-sweep 1.2s ease .2s forwards;}
@keyframes g-sweep{to{clip-path:inset(0 0 0 0);}}

/* B · BUILD — squares pop in one by one */
.dos .gauge.build .sq{opacity:0;transform:translateY(.3em) scale(.5);
  animation:g-build .34s cubic-bezier(.2,1.5,.4,1) forwards;animation-delay:calc(.45s + var(--i) * .09s);}
@keyframes g-build{to{opacity:1;transform:none;}}

/* C · CHARGE — squares flash bright, then settle, cascading */
.dos .gauge.charge .sq{opacity:.12;animation:g-charge .55s ease forwards;animation-delay:calc(.85s + var(--i) * .075s);}
@keyframes g-charge{
  0%{opacity:.12;}
  45%{opacity:1;text-shadow:0 0 12px var(--grn),0 0 4px #eafff4;}
  100%{opacity:1;text-shadow:0 0 6px rgba(39,240,138,.18);}
}
.dos .for{margin-top:.9rem;border-top:1px solid var(--line);padding-top:.7rem;font-size:.85rem;color:var(--dim);
  text-transform:uppercase;letter-spacing:.08em;}
.dos .for b{color:var(--ink);}

/* ── header feed: datamosh glitch over a rolling distortion band ───────── */
/* keep the dossier text crisp above the grain + line layers */
.dos .top > div{position:relative;z-index:4;}

/* continuously rolling distortion band — the moving lines */
.dos .top::after{
  content:"";position:absolute;left:0;right:0;height:26%;top:-26%;z-index:3;
  pointer-events:none;mix-blend-mode:screen;
  background:repeating-linear-gradient(0deg, rgba(255,255,255,.12) 0 1px, rgba(0,0,0,.30) 1px 3px);
  animation:line-roll 2.4s linear infinite;
}
@keyframes line-roll{0%{top:-26%;}100%{top:100%;}}

/* animated film grain over the image */
.dos .top::before{
  content:"";position:absolute;inset:-12%;z-index:1;pointer-events:none;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:160px;mix-blend-mode:overlay;opacity:.5;
  animation:grain .3s steps(3) infinite;
}
@keyframes grain{0%{transform:translate(0,0);}25%{transform:translate(-3%,2%);}50%{transform:translate(2%,-3%);}75%{transform:translate(-2%,3%);}100%{transform:translate(3%,-1%);}}

/* Wreck-It-Ralph glitch bursts — RGB split + slice-tear, idle then snap */
.dos .top{animation:datamosh 5s steps(1) infinite;}
@keyframes datamosh{
  0%,80%,100%{transform:translateX(0);filter:none;clip-path:none;}
  81%   {transform:translateX(-7px);filter:drop-shadow(3px 0 #ff0044) drop-shadow(-3px 0 #00e9ff);}
  82.5% {transform:translateX(7px);clip-path:inset(18% 0 40% 0);}
  84%   {transform:translateX(-5px);clip-path:inset(56% 0 6% 0);filter:drop-shadow(-4px 0 #ff0044) drop-shadow(4px 0 #00e9ff);}
  85.5% {transform:translateX(4px);clip-path:inset(6% 0 62% 0);}
  87%   {transform:translateX(-6px);filter:saturate(2.4) hue-rotate(80deg);}
  88%   {transform:translateX(0);clip-path:none;filter:none;}
}

/* ── book cover: original diagonal scanner sheen (unchanged) ───────────── */
.dos .vid{overflow:hidden;}
.dos .vid::before{
  content:"";position:absolute;top:-60%;bottom:-60%;left:0;width:32%;z-index:2;
  pointer-events:none;mix-blend-mode:screen;
  background:linear-gradient(90deg, transparent, rgba(189,247,216,.32) 50%, transparent);
  animation:scan-sheen 5s ease-in-out 1.4s infinite;
}
@keyframes scan-sheen{
  0%      {transform:translateX(330%) skewX(-18deg);opacity:0;}
  8%      {opacity:1;}
  48%     {transform:translateX(-210%) skewX(-18deg);opacity:1;}
  52%,100%{transform:translateX(-210%) skewX(-18deg);opacity:0;}
}

@media (prefers-reduced-motion:reduce){
  .dos .gauge.sweep b{clip-path:none;}
  .dos .gauge .sq{opacity:1 !important;transform:none !important;animation:none !important;}
  .dos .top,.dos .top::before,.dos .top::after,.dos .vid::before{animation:none;}
  .dos .top::before{opacity:.3;}
  .dos .vid::before{opacity:0;}
}
</style>
