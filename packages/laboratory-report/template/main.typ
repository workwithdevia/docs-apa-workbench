// Starter entrypoint. Normally edit YAML and sections, not this file.
#import "@preview/nexum-apa-lab-report:0.1.0": apa-lab-report
#import "content.typ": report-content

#let metadata = yaml("metadata.yaml")
#let settings = yaml("settings.yaml")

#show: apa-lab-report.with(
  metadata: metadata,
  settings: settings,
  content: report-content,
  bibliography-file: path("references.bib"),
)
