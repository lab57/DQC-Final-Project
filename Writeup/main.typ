
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
  

  Distributed Quantum Computing provides a promising approach for a practical quantum computer on a shorter timescale than would otherwise be possible. Interconnecting small quantum processing units (QPUs) through quantum links facilitates large quantum circuits being distributed across the network, which introduces the problem of compiling a given circuit for the specific architecture, with appropriately inserted SWAPs and EPR pair generation as necessary. Past work (@Promponas_Mudvari_Chiesa_Polakos_Samuel_Tassiulas_2024 and @Burt_Chen_Leung_2024) have shown promising approaches to this problem using reinforcement learning and genetic algorithms, respectively. However, the papers provde no standardized metric to directly compare the methods performance. In this work, the results of the papers are reproduced, and their performance on a standardized metric is compared to see their viability on tackling the problem in practical settings.


  
  #v(1.3em)
]

= Introduction & Background



= Implementations

== Reinforcement Learning
=== Introduction
The first approach models the compilation problem as a Markov Decision Process (MDP), so that modern reinforcement algorithms can be applied. These algorithms have seen great success and popularity in recent years (e.g. in large language models), and re well-suited to attempt the compilation problem.



=== Implementation 
Based on the details and specifications described in the RL paper @Promponas_Mudvari_Chiesa_Polakos_Samuel_Tassiulas_2024, I reimplemented the environemnt using `gymnasium` so that I could train using the implementations of DDQ and PPO found in the `stable-baselines3` library.





== Genetic Algorithm




= Performance Comparison

= Discussion & Conclusion