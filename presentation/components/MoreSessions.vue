<script setup lang="ts">
// public/ asset resolved through Vite's configured base so the deploy sub-path
// (--base /Extending-Your-Agent/) is honoured at build time.
const cover = `url(${import.meta.env.BASE_URL}cover.jpg)`

const badgeText = { current: 'YOU ARE HERE', scheduled: 'SCHEDULED', proposed: 'PROPOSED' }
const badgeClass = { current: 'badge--now', scheduled: 'badge--talk', proposed: 'badge--red' }

const sessions = [
  { date: '1 Sep 2026',  title: 'RAG & Embeddings',                         status: 'current' },
  { date: '1 Oct 2026',  title: 'MCP Servers: Is This How Skynet Started?', status: 'scheduled' },
  { date: '25 Nov 2026', title: 'Predicting Mental Fatigue Using AI',        status: 'scheduled' },
  { date: 'Dec 2026',    title: 'The Math Behind the AI Curtain',            status: 'scheduled' },
  { date: 'TBD',         title: 'Agent Cage Match & Model Bake-Off',         status: 'proposed' },
  { date: 'TBD',         title: 'Text-to-SQL & Semantic Search',            status: 'proposed' },
]
</script>

<template>
  <div class="evil" :style="{ '--cover': cover }">
    <div class="pad">
      <div class="term">
        <div class="banner">
          <BootLog />
          <div class="hal"><HalEye /></div>
          <h1 class="heading">More AI Sessions</h1>
        </div>
        <div class="body">
          <div class="rows">
            <div v-for="s in sessions" :key="s.title" class="row">
              <span class="mark">▸</span>
              <span class="date" :class="{ tbd: s.status === 'proposed' }">{{ s.date }}</span>
              <span class="nm">{{ s.title }}</span>
              <span class="badge" :class="badgeClass[s.status]">{{ badgeText[s.status] }}</span>
            </div>
          </div>
          <div class="prompt">&gt; the resistance needs presenters — enlist now<span class="cursor">█</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
</style>

<style scoped>
.evil{
  --bg:#07070a; --bg2:#0e0e15; --red:#ff1f3d; --red-deep:#b3001b;
  --glow:rgba(255,31,61,.55); --line:rgba(255,31,61,.22);
  --green:#36ff9b; --text:#c9ccd4; --dim:#6b7180;
  --display:'Orbitron','IBM Plex Mono',monospace;
  --mono:'IBM Plex Mono',monospace;
  position:absolute;inset:0;
  background:radial-gradient(130% 130% at 50% -10%, var(--bg2), var(--bg) 60%);
  color:var(--text);font-family:var(--mono);
}
.pad{height:100%;box-sizing:border-box;padding:1.6rem 2rem;}
.term{
  height:100%;display:flex;flex-direction:column;overflow:hidden;position:relative;
  border-radius:7px;
  box-shadow:0 0 40px rgba(255,31,61,.07);
  /* the full terminator image fills the whole window; a scrim darkens the lower
     half so the session list stays readable as the image continues behind it */
  background:
    linear-gradient(to bottom,
      rgba(7,7,10,.25) 0%,
      rgba(7,7,10,.18) 28%,
      rgba(7,7,10,.34) 46%,
      rgba(7,7,10,.60) 64%,
      rgba(7,7,10,.82) 82%,
      rgba(7,7,10,.92) 100%),
    var(--cover) center/cover no-repeat,
    rgba(8,8,12,.72);
}

/* top band — heading + chrome over the visible upper image (no own background) */
.banner{position:relative;flex:0 0 48%;}
.hal{position:absolute;top:.6rem;right:.8rem;z-index:2;transform:scale(.55);transform-origin:top right;}

.heading{
  position:absolute;left:1.6rem;right:1rem;bottom:.6rem;z-index:2;margin:0;
  font-family:var(--display);text-transform:uppercase;letter-spacing:.04em;
  font-weight:700;font-size:3rem;line-height:1.02;
  background:linear-gradient(100deg,#8c0016 0%,#ff1f3d 25%,#ff7a4d 44%,#fff 50%,#ff7a4d 56%,#ff1f3d 75%,#8c0016 100%);
  background-size:220% auto;-webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;color:transparent;
  filter:drop-shadow(0 0 14px var(--glow)) drop-shadow(0 2px 12px rgba(0,0,0,.95));
  animation:sheen 5s linear infinite;
}
@keyframes sheen{ to{ background-position:220% center; } }

.body{position:relative;z-index:1;padding:1.1rem 1.9rem;flex:1;display:flex;flex-direction:column;}
.rows{display:flex;flex-direction:column;gap:.45rem;}
.row{display:grid;grid-template-columns:2.4rem 8rem 1fr auto;gap:1rem;align-items:center;font-size:1rem;}
.mark{color:var(--red);text-shadow:0 0 6px var(--glow);font-size:2.1rem;line-height:1;}
.date{color:var(--text);letter-spacing:.04em;font-size:.92rem;}
.date.tbd{color:var(--dim);}
.nm{color:#fff;}
.prompt{margin-top:auto;padding-top:.8rem;color:var(--dim);letter-spacing:.08em;font-size:.92rem;}
.cursor{color:var(--red);animation:blink 1.05s steps(1) infinite;}
@keyframes blink{50%{opacity:0;}}

.badge{
  font-family:var(--display);font-size:.56rem;letter-spacing:.16em;
  border:1px solid var(--red);color:var(--red);padding:.3em .65em;border-radius:3px;
  white-space:nowrap;justify-self:end;
  box-shadow:inset 0 0 10px rgba(255,31,61,.15), 0 0 10px rgba(255,31,61,.12);
}
.badge--talk{border-color:var(--green);color:var(--green);
  box-shadow:inset 0 0 10px rgba(54,255,155,.12), 0 0 10px rgba(54,255,155,.1);}
.badge--red{border-color:var(--red);color:var(--red);}
.badge--now{border-color:#fff;color:#fff;
  box-shadow:inset 0 0 10px rgba(255,255,255,.18), 0 0 14px rgba(255,255,255,.22);}

@media (prefers-reduced-motion:reduce){.heading,.cursor{animation:none;}}
</style>
