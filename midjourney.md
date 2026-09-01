Midjourney prompts
==================

Art direction for the RAG & Embeddings deck: **risograph duotone**, fluorescent orange
(`#e84700` / `#e78200`) on charcoal (`#343434`) — the theme palette from
[`presentation/theme/styles/index.css`](presentation/theme/styles/index.css).

Every fenced block below is one prompt, submitted as-is by the `midjourney-submit` skill.

# Style lock

The cover prompts run text-only to find the look. Pick the winner, then append
`--sref <winning image URL> --sw 100` to every later prompt so the deck stays coherent.
Drop to `--sw 50` where the style buries the subject.

# Cover art

Sits in the `cover` layout's image slot: 35% width, full height, `object-fit: contain`, on an
`#E78200` ground — so portrait `--ar 2:3`, and the art needs its own charcoal ground or it
dissolves into the slide.

```
risograph print, an open book whose pages become a night sky of scattered plotted points and faint connecting lines, two-colour fluorescent orange and charcoal, halftone grain, visible misregistration, bold flat shapes, no text --ar 2:3 --style raw
```

```
risograph print, a dense constellation of dots forming loose clusters, one dot ringed and haloed, thin lines to its nearest neighbours, flat charcoal ground with fluorescent orange overprint, halftone texture, misregistration, no text --ar 2:3 --style raw
```

```
risograph print, silhouette of a human head in profile filled with a field of scattered dots and contour lines like a topographic map, two-colour orange and charcoal, coarse halftone grain, screenprint texture, no text --ar 2:3 --style raw
```

```
risograph poster, a library card catalog drawer bursting open into a swarm of floating dots, flat geometric shapes, fluorescent orange on charcoal, misregistered layers, grainy paper texture, no text --ar 2:3 --style raw
```

# Section backgrounds

Full-bleed in the `section` layout: `object-fit: cover` at 16:10 under a 45% black overlay,
with the white title set top-left. So `--ar 16:10`, keep the top-left half quiet, and push the
orange brighter than the cover — the overlay eats 45% of it.

Both take `--sref <cover art URL> --sw 100` appended before submitting.

## RAG

```
risograph print, a hand lifting one glowing page out of a wall of dark archive drawers, the page bright fluorescent orange, everything else charcoal, halftone grain, misregistration, flat shapes, empty dark space upper left, no text --ar 16:10 --style raw
```

## Embeddings

```
risograph print, a vast field of scattered dots drifting into loose clusters across a dark plane, contour lines like a topographic map beneath them, fluorescent orange on charcoal, halftone grain, misregistration, empty dark space upper left, no text --ar 16:10 --style raw
```

# Tech Lunch

Left column of `two-col-image-text`: half width, full height, `object-fit: contain` on white —
so portrait `--ar 2:3`, and like the cover art it needs its own charcoal ground or it dissolves
into the slide. Resize to 800x1200 before committing:

```bash
bun run presentation/theme/scripts/resize-image.ts <download> tech-lunch --width 800 --height 1200
```

All four take `--sref <cover art URL> --sw 100` appended before submitting. Same locked
risograph style as the rest of the deck — only the metaphor varies, since four different
aesthetics would break the deck rather than give you a choice.

```
risograph print, a stack of sandwiches rendered as glowing layered strata with sparks and speech bubbles rising from between the layers, fluorescent orange on charcoal, halftone grain, misregistration, flat bold shapes, no text --ar 2:3 --style raw
```

```
risograph print, a lunch table seen from directly above, plates and cups connected by bright wires into a small constellation, fluorescent orange on charcoal, coarse halftone, misregistered layers, no text --ar 2:3 --style raw
```

```
risograph print, a paper lunch bag torn open with a burst of lightning bolts and geometric shapes erupting out of it, flat shapes, fluorescent orange on charcoal, screenprint texture, grain, no text --ar 2:3 --style raw
```

```
risograph print, five silhouetted figures leaning over a table, one standing mid-gesture explaining, an orange glow between them, everything else charcoal, halftone grain, misregistration, no text --ar 2:3 --style raw
```
