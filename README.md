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


## Stardew Valley Tree Dynamics as a Cellular Automaton

Basically, a [Cellular Automaton](https://en.wikipedia.org/wiki/Cellular_automaton) is a grid of cells (or lattice represented by integer points $\mathbb{Z}^n$). Each cell contains a value, representing the state of that cell. In a cellular automaton, the states are also discrete and can be represented as integers. Let's call a grid with a specific choice of state for each cell, a configuration of the grid (sometimes this is also called a state). The states change over time but time is discrete as well. How the grid changes is determined by applying a *transition rule* or *update rule* to its current configuration. This transition rule plays the same role as an equation of motion or other. Stardew valley trees are a good example of how cellular automata can represent real-world phenomena, even when those phenomena aren't really discrete. The trees occupy positions on a lattice and the lattice has a state for each tree growth stage and a state for empty ground. Note we can simply add more states to represent other tree species or grass, etc.  Here's an example

![Lattice with colored and numbered cells](./images/cells_with_numbers_colors.png)

While in principle one could define a transition rule that is any function maps configurations to other configurations, in practice it is more interesting to use transition rules which are defined **locally**. That means, for a given cell, its change in state during one transition depends only on its current state and the state of nearby cells. For example, in the grid below, the next state of the blue cell depends on its current state and the current state of the surrounding gray cells. 


![Lattice with colored and numbered cells](./images/neighborhood_moore.png)

If we define a local transition rule for each **neighborhood**, we can apply this rule for every cell and its neighborhood to define a transition rule for an entire grid. Note we sometimes have to make special choices for the boundary of the grid, similar to boundary conditions for differential equations. We can vary the neighborhood for rules that have a longer distance spatial interaction. 

![von neumann neghborhood](./images/neighborhood_compass.png)


![two layer moore neghborhood](./images/neighborhood_big_moore.png)





In many physical systems, we wish represent to how some quantity varies in space and time in a region of space. Think for instance how an electric and magnetic field. Or the distribution of temperature and pressure. Or in this case, the distribution of trees by various growth stages. There are several common ways to represent such systems mathematically. A quick way to classify them is by asking if states, time, space are discrete or continuous. Continuous states, time, or space means we can use $n$_tuples of real numbers $\mathbb{R}^n$ instead of integers $\mathbb{Z}^n$. Cellular automata are what you get when all three are discrete. You can see some other examples.


|      |            | Space                       |                                 |                                           |                                |
| ---- | ---------- | --------------------------- | ------------------------------- | ----------------------------------------- | ------------------------------ |
|      |            | Discrete                    |                                 | Continuous                                |                                |
|      |            | Discrete States             | Continuous States               | Discrete States                           | Cont. States                   |
| Time | Discrete   | Cellular Automata           | Iterated Maps/Functions         | Integral Equations                        | Integral Equations             | 
|      | Continuous | Markov Processes (via prob) | Ordinary Differential Equations | Partial Differential Equations (via prob) | Partial Differential Equations |


Although these mathematical representations of the same physical systems are very different, they often serve as good approximations for one another. Sometimes by converting from one form to another, we get new insight. However, this has to be done with care, because not all cellular automata can be represented as a partial differential equation, so there might not be any conversion. But usually interesting physical systems have symmetries or other properties that make this conversion possible. For instance, cellular automata usually have translational symmetries and rotational symmetries with their grid. At large scales, these symmetries approximate the continuous symmetries of continuous space. The local transition rules of cellular automata correspond to the local rules of partial differential equations. We can also use different grids, so hexagonal grids or triangular grids are also possible for cellular automata, but more complicated to program. It turns out that the emergent properties of interesting physical systems often do not depend strongly such choices.

## How do trees grow? 

![markov chain for growth](./images/markov_chain_for_growth.png)
