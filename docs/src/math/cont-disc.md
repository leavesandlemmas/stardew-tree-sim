# Continuous or Dicrete Systems ?

In Biology, Physics and a number of sciences, we often wish to represent to how 
some quantity varies in space and time. 
Think for instance how an electric and magnetic field. Or the distribution of 
temperature and pressure. Or in this case, the distribution of trees by various 
growth stages. There are families of mathematical models which we can classify 
by whether states, time, space are discrete or continuous.

Continuous states, time, or space essentially means we can use $n$-tuples of real
numbers $\mathbb{R}^n$ instead of integers $\mathbb{Z}^n$ on a lattice. 

Partial differential equations have continuous states with
varying over a continuous space with continuous time.  For example, the heat equation
specifies how the temperature $T$ varies over a continuous space (like 3D volumes)
with continuous time.  

\\[ \frac{\partial T}{\partial t} = \alpha \frac{\partial^2 T}{\partial x^2} \\]

Cellular automata are what you get when all three are discrete. 
You can see some other examples.


|      |            | Space                       |                                 |                                           |                                |
| ---- | ---------- | --------------------------- | ------------------------------- | ----------------------------------------- | ------------------------------ |
|      |            | Discrete                    |                                 | Continuous                                |                                |
|      |            | Discrete States             | Continuous States               | Discrete States                           | Cont. States                   |
| Time | Discrete   | Cellular Automata           | Iterated Maps/Functions         | Integral Equations                        | Integral Equations             | 
|      | Continuous | Markov Processes (via prob) | Ordinary Differential Equations | Partial Differential Equations (via prob) | Partial Differential Equations |