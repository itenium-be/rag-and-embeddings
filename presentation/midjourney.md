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
