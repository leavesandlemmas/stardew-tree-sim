#!/usr/bin/env python3
import os
import argparse
import logging
import h5py
import numpy as np
import matplotlib.pyplot as plt

# constants
background_color = np.array([255, 246, 229]) / 255
tree_color = np.array([2, 62, 16]) / 255
mort_prob = 0.01
reprod_prob = 0.15


def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Visualize simulation results from an HDF5 or NPY file.')
    parser.add_argument('data_path', type=str, help='Path to the simulation data file (.hdf5 or .npy).')
    return parser.parse_args()


def setup_logging():
    """
    Sets up logging for the script.
    """
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)


def color(arr: np.ndarray) -> np.ndarray:
    """set color of tree stages
    
    Parameters
    ----------
    arr : np.ndarray
        The simulation data.
    
    Returns
    -------
    np.ndarray
        The color-encoded simulation data.
    """
    out = np.empty(arr.shape + (3,))
    stage = arr/5
    for i in range(3):
        out[...,i] = background_color[i]*(1 - stage) + tree_color[i]*stage
    return out


def count(arr: np.ndarray) -> np.ndarray:
    """count the number of each tree stage
    
    Parameters
    ----------
    arr : np.ndarray
        The simulation data.
    
    Returns
    -------
    np.ndarray
        The counts of each tree stage.
    """
    shape = arr.shape[0], 6
    out = np.empty(shape,dtype='int64')
    for s in range(6):
        out[:,s] = (arr == s).sum(axis=(1,2))
    return out


def load_simulation_data(filename: str) -> np.ndarray:
    """
    Loads simulation data from a numpy file.

    Parameters
    ----------
    filename : str
        The name of the file to load.

    Returns
    -------
    np.ndarray
        The data from the file.
    """
    file_path = os.path.normpath(filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No file found at {file_path}")
    # if file is hdf5 or h5, use h5py to read the dataset
    # if file is npy, use np.load to read the file
    # others, raise an error
    if file_path.endswith('.hdf5') or file_path.endswith('.h5'):
        with h5py.File(file_path, 'r') as f:
            data = f['TreeGrowthData'][:]
    elif file_path.endswith('.npy'):
        data = np.load(file_path)
    else:
        raise ValueError("Unsupported file format")
    
    return data


def plot_population_and_stages(
        counts: np.ndarray,
        N: np.ndarray,
        Kmax: int,
        iterations: np.ndarray,
    ):
    """
    Plots population size, tree stages, and grid size over iterations.

    Parameters
    ----------
    counts : np.ndarray
        The counts of each tree stage.
    N : np.ndarray
        The population size.
    Kmax : int
        The maximum grid size.
    iterations : np.ndarray
        The iterations to mark on the plot.
    """
    fig, ax = plt.subplots(1, 3, sharex='row', figsize=(12, 3))
    
    ax[0].plot(N, label='Pop Size')
    ax[0].plot(counts[:, 0], '--', label='Empty')
    ax[0].axhline(Kmax, color='r', ls='dotted', label='Grid Size')
    ax[0].axhline(Kmax * (1 - mort_prob / reprod_prob), color='C0', ls='dotted')

    for s in [4, 5]:
        ax[1].plot(counts[:, s], label=f"s={s}")
    ax[1].axhline(Kmax * 0.1772 * (1 - mort_prob / reprod_prob), color='C1', ls='--')
    ax[1].axhline(Kmax * 0.7792 * (1 - mort_prob / reprod_prob), color='C0', ls='--')

    for s in [1, 2, 3]:
        ax[2].plot(counts[:, s], label=f"s={s}")

    for axi in ax.ravel():
        for iteration in iterations:
            axi.axvline(iteration, ls='dashdot', color='k')
        axi.grid()
        axi.legend()
        axi.set_xlabel('Iterations')

    fig.tight_layout()
    plt.show()


def visualize_grid_states(arr_color: np.ndarray, iterations: np.ndarray):
    """
    Visualizes the grid states at specified iterations.

    Parameters
    ----------
    arr_color : np.ndarray
        The color-encoded simulation data.
    iterations : np.ndarray
        The iterations at which to display the grid states.
    """
    fig, ax = plt.subplots(1, 4, sharex='row', sharey='row', figsize=(16, 4))
    for i, iteration in enumerate(iterations):
        ax[i].set_title(f"Iteration: {iteration}")
        ax[i].imshow(arr_color[iteration])
    fig.tight_layout()
    plt.show()


def main():
    """Main function for the visualization script."""
    # Setup logging
    setup_logging()
    logging.info("Starting the visualization script.")

    # Parse command-line arguments
    args = parse_arguments()
    logging.info(f"Loading simulation data from: {args.data_path}")

    # Load the simulation data
    try:
        arr = load_simulation_data(args.data_path)
        logging.info("Data loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return

    # Process and visualize the data
    try:
        # Color encode the simulation data
        arr_color = color(arr)
        logging.info("Color encoding completed.")

        # Count stages
        counts = count(arr)
        N = counts[:, 1:].sum(axis=1)
        Kmax = arr.shape[1] * arr.shape[2]
        nint = 4
        iterations = np.linspace(arr.shape[0] / (nint + 1), nint * arr.shape[0] / (nint + 1), nint)
        iterations = iterations.astype('int64')

        # Plot the population trends and stages
        logging.info("Plotting population trends and tree stages.")
        plot_population_and_stages(counts, N, Kmax, iterations)

        # Visualize the grid states
        logging.info("Visualizing grid states.")
        visualize_grid_states(arr_color, iterations)

        logging.info("Visualization completed successfully.")
    except Exception as e:
        logging.error(f"Error during processing or visualization: {e}")



if __name__ == "__main__":
    main()