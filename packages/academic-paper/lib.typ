#import "@preview/nexum-apa-core:0.1.0": compose-document, render-academic-content
#import "@preview/nexum-apa-core:0.1.0": apa-figure, apa-table, apa-note, apa-run-in-heading

#let apa-paper(
  body,
  metadata: (:),
  settings: (:),
  content: (:),
  bibliography-file: none,
) = {
  let language = settings.at("language", default: "es")
  let abstract = content.at("abstract", default: none)
  let keywords = metadata.at("keywords", default: ())
  let rendered = render-academic-content(content, language: language)

  compose-document(
    rendered + body,
    metadata: metadata,
    settings: settings,
    abstract: abstract,
    keywords: keywords,
    bibliography-file: bibliography-file,
  )
}
