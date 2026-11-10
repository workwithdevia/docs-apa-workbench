# nexum-apa-paper

APA-oriented academic paper starter. The package delegates typography and
shared components to `nexum-apa-core`.

After `nexum-apa-core` is accepted by Typst Universe, instantiate with:

```bash
typst init @preview/nexum-apa-paper:0.1.0
```

Edit `metadata.yaml`, `settings.yaml`, `content.typ`, the files in `sections/`,
and `references.bib`. `main.typ` should normally remain unchanged.

The monorepo stores this package in `packages/academic-paper/`; its published
Typst identifier is `nexum-apa-paper`.
