# stardew-tree-sim

A stochastic cellular automaton modeling how trees grow and spread inspired by 
*Stardew Valley*. A conceptual model for questions from mathematical
ecology: how fast do populations fill space, can they go extinct, and
which species win when several compete?

![Forest on a Stardew Valley farm](./docs/src/images/20231018082043_1.jpg)

<!-- Replace or supplement with an animated GIF of the simulation running.
     It's the single most effective thing a portfolio README can show. -->

## Highlights

- **Model:** trees occupy cells on a grid and move through five growth
  stages (seed → seedling → bush → sapling → mature), spreading seeds into
  neighboring cells under a local stochastic update rule.
- **Analysis:** Markov chain treatment of growth and extinction dynamics.
- **Implementation:** convolution-based neighbor counting for fast updates
  over large grids, with configurable neighborhoods (Moore, von Neumann,
  extended Moore) and boundary conditions.

## Quick start

​```bash
cargo add stardew-tree-sim
cargo run --example basic
​```

​```rust
// Minimal usage example
use stardew_tree_sim::Grid;

let mut grid = Grid::new(64, 64);
grid.step();
​```

## Documentation

- **[The book](https://<you>.github.io/stardew-tree-sim/)** covers the
  game mechanics, the cellular automaton model, and the mathematics
  behind the analysis.
- **[API docs](https://docs.rs/stardew-tree-sim)** on docs.rs.

## Results

<!-- One chart or a sentence or two of findings, e.g. population over time
     or time-to-saturation vs. grid size. Link to the book chapter. -->

## License

MIT