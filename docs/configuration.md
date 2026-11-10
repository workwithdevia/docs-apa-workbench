# Configuration reference

The generated project has four main author-facing inputs: metadata, settings,
content manifest, and bibliography.

## `metadata.yaml`

```yaml
title: "Document title"
authors:
  - "First Author"
  - "Second Author"
affiliation: "Department or affiliation"
faculty: "Faculty"
institution: "University"
program: "Degree program"
course: "Course code and name"
instructor: "Instructor"
date: "10 November 2026"
laboratory: "Laboratory name"
practice: "Experiment or practice"
group: "Group identifier"
keywords:
  - "keyword one"
  - "keyword two"
```

All fields except the title are optional in the core schema. The academic-paper
and laboratory-report templates decide which fields they expose on the cover.

## `settings.yaml`

```yaml
language: "en" # or "es"

page:
  paper: "us-letter"
  margin-in: 1
  page-numbers: true

typography:
  text:
    font: "New Computer Modern"
    size-pt: 10
    top-edge-em: 0.8
    bottom-edge-em: -0.2
  math:
    font: "New Computer Modern Math"
    # size-pt: 10 # optional
  code:
    font: "DejaVu Sans Mono"
    inline-size-em: 0.85
    block-size-pt: 9
  paragraph:
    justify: false
    leading-em: 1
    spacing-em: 1
    first-line-indent-in: 0.5
    heading-leading-em: 1
    heading-spacing-em: 1

cover:
  top-space-em: 3

bibliography:
  style: "apa"
  full: false
```

Text, math, and code are independent typographic systems. Custom fonts must be
available to the compiler. In Typst.app, upload `.ttf` or `.otf` files to the
project and verify the internal family name in the font picker. The package does
not install fonts.

## `content.typ`

The content manifest maps semantic section keys to included section files. The
library owns the display order and localized labels. Use `none` to omit an
optional section.

Laboratory keys: `abstract`, `introduction`, `theoretical_framework`,
`objectives`, `materials_methods`, `results`, `discussion`, `conclusion`,
`appendices`.

Academic keys: `abstract`, `introduction`, `literature_review`, `method`,
`results`, `discussion`, `conclusion`, `acknowledgments`, `appendices`.

The introduction is not assigned a separate heading by default: the document
title is repeated at the beginning of the body, following the student-paper
convention described by APA.
