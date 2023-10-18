# stardew-tree-sim
This repository is a project that explores a simulation and mathematical analysis of a simplified model of tree dynamics, based on how trees grow and spread in the video game [Stardew Valley](https://www.stardewvalley.net/). 

## Overview of a Stardew Valley Forest


![Forest on stardew valley farm](./images/20231018082043_1.jpg)

THe screenshot above shows an example of the vegetation on a farm in Stardew Valley. There are several types of trees, grass, and other vegetation. The trees and grass naturally spread to fill available space. Thinking like a biologist, we might wonder: How quickly do the trees fill area? Can the tree populations go extinct? Given several types of trees, will one of the tree species eventually go extinct? While certainly not needed to play the game, answers to these questions give insight into more serious questions in mathematical biology. These questions are the kind we might use a model of real world tree populations to study. In either case, we have to figure out how to calculate the emergent properties of these dynamics. 

First, let's note that the dynamics occur on a grid. You can see a red square that indicates one cell of this grid.

![Close up of forest, showing a red square of one cell](./images/treegrid_latent.jpg)

If we draw the grid, we see that each individual tree, tuff of grass, bush, and so on occupy a single cell in a grid. 

![Close up of forest, superimposed red grid](./images/treegrid.jpg)

If we focus on the trees, we see that there are five stages of living trees. The first four are a **planted seed** (stage 1), a germinate **seedling** (stage 2), a **bush** form (stage 3), and a **sapling** (stage 4).   

![Four stages of a growing tree](./images/tree_stages_1_to_4.jpg)

The fifth stage is a mature tree (stage 5). Trees can die and leave stumps not shown. 

![A mature tree](./images/tree_mature.jpg)

Because there is a discrete set of stages on a discrete,  we can represent the tree population dynamics using cellular automata.


### Cellular Automata (discrete time, discrete space models)
A short primer on Cellular Automata. In many physical systems, we wish represent to how something changes in time in a region of space. Think for instance how an electric and magnetic field can vary through out a region in space. These variations then lead to changes over time in the fields. There are several common ways to represent such systems mathematically. We'll classify them by asking whether or not time and space are discrete or continuous. Continuous time and space means we can use real numbers $\mathbb{R}^n$ to index points in space or in time. Discrete time and space means that we only get integers $\mathbb{Z}^n$, that is everything happens on a grid (and a 1D grid for time). Cellular automata are dynamic models with local spatial interactions.


|      |            | Space                       |                                 |                                           |                                |
| ---- | ---------- | --------------------------- | ------------------------------- | ----------------------------------------- | ------------------------------ |
|      |            | Discrete                    |                                 | Continuous                                |                                |
|      |            | Discrete States             | Continuous States               | Discrete States                           | Cont. States                   |
| Time | Discrete   | Cellular Automata           | Iterated Maps/Functions         | Integral Equations                        | Integral Equations             | 
|      | Continuous | Markov Processes (via prob) | Ordinary Differential Equations | Partial Differential Equations (via prob) | Partial Differential Equations |




## How do trees grow? 

