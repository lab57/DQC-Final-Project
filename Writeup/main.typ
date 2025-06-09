
#import "template.typ": *
#import "@preview/physica:0.9.5" : *
#import "@preview/diagraph:0.3.3" : *
// Take a look at the file `template.typ` in the file panel
// to customize this template and discover how it works.
#show: project.with(
  title: [Performance Evaluation of Reinforcement Learning\ and Genetic Algorithm Based Compilers\ for Distributed Quantum Systems],
  authors: (
    (name: "Luc Barrett", email: "labarrett@umass.edu", affiliation: [CS692QC: Distributed Quantum Computing \ Final Project Report]),
  ),
  // Insert your abstract after the colon, wrapped in brackets.
  // Example: `abstract: [This is my abstract...]`
  // abstract: lorem(59),
  date: "May 12, 2025",
)


// We generated the example code below so you can see how
// your document will look. Go ahead and replace it with
// your own content!



#place(top + center, float: true, scope: "parent")[
  #set align(center)
  #smallcaps(text(weight: 800, size: 14pt)[Abstract])\
  #lorem(75) 
  #v(1.3em)
]

= Introduction & Background

= Reinforcement Learning Approach

= Genetic Approach



= Performance Comparison

= Discussion & Conclusion