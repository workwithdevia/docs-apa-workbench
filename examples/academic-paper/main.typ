// Starter entrypoint. Normally edit YAML and sections, not this file.
#import "@preview/nexum-apa-paper:0.1.0": apa-paper
#import "content.typ": paper-content

#let metadata = yaml("metadata.yaml")
#let settings = yaml("settings.yaml")

#show: apa-paper.with(
  metadata: metadata,
  settings: settings,
  content: paper-content,
  bibliography-file: path("references.bib"),
)
