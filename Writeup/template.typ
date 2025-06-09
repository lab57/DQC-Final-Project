// The project function defines how your document looks.
// It takes your content and some metadata and formats it.
// Go ahead and customize it to your liking!
#let project(
  title: "",
  abstract: [],
  authors: (),
  date: none,
  body,
) = {
  // Set the document's basic properties.
  set document(author: authors.map(a => a.name), title: title)
  set page(
    paper: "us-letter",
    margin: (left: 15mm, right: 15mm, top: 20mm, bottom: 20mm),
    // margin: (left: 20mm, right: 20mm, top: 30mm, bottom: 30mm),
    
    numbering: "1",
    number-align: center,
  )

  set page(fill: rgb(20, 20,30 ))
  set text(fill: white)



  // Save heading and body font families in variables.
  let body-font = "New Computer Modern"
  let sans-font = "New Computer Modern Sans"
  set math.equation(numbering: "(1)")

  // Set body font family.
  set text(font: body-font, lang: "en")
  show math.equation: set text(weight: 400)

  // Set paragraph spacing.
  show par: set block(above: 0.75em, below: 0.75em)

  show heading: set text(font: sans-font)

  // Set run-in subheadings, starting at level 3.
  show heading: it => {
    if it.level > 2 {
      parbreak()
      text(11pt, style: "italic", weight: "regular", it.body + ".")
    } else {
      it
    }
  }
  // tight: 0.58
  set par(leading: 0.65em)

  // Title row.
  align(center)[
    #block(text(font: sans-font, weight: 700, 1.75em, title))
    #v(1em, weak: true)

    // #date
  ]
v(1em)
  // Author information.
  pad(
    top: 0.3em,
    bottom: 0.3em,
    x: 2em,
    grid(
      columns: (1fr,) * calc.min(3, authors.len()),
      gutter: 1em,
      ..authors.map(author => align(center)[
        *#author.name* \
        #author.email \
        #author.affiliation
      ]),
    ),
  )
  v(1em)
  // Main body.
  set par(justify: true)
  show: columns.with(2, gutter: 1em)

  // heading(outlined: false, numbering: none, text(0.85em, smallcaps[Abstract]))
  abstract

  set heading(numbering: "1.")

  set image(width: 90%)
  set figure(placement: auto)
  //set text(size: 12pt)
  show figure: set text(size: 10pt)


  body

  colbreak()
  // show bibliography: set heading(numbering: "1.")
  bibliography("cited.bib", full: true, style: "institute-of-electrical-and-electronics-engineers", )
}