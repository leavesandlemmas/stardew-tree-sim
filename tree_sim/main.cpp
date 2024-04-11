#include <H5Cpp.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <tbb/tbb.h>

#include <array>
#include <filesystem>
#include <iostream>
#include <random>
#include <vector>

#include "spdlog/spdlog.h"

// Define the grid size and other constants
constexpr size_t ntree = 5;
constexpr size_t num = 120;  // 12*10, using a linear dimension
constexpr size_t iterations = 100;
constexpr size_t width = 4 * num;  // aspect ratio 4:3
constexpr size_t height = 3 * num;
const double reprod_prob = 0.15;
const double grow_prob = 0.2;
const double mort_prob = 0.01;

// Define the neighborhood for growth and reproduction kernels
const std::vector<std::vector<int>> growth_neighborhood = {
    {1, 1, 1},
    {1, 0, 1},
    {1, 1, 1}};
const std::vector<std::vector<int>> reprod_neighborhood = {
    {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 0, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1},
    {1, 1, 1, 1, 1, 1, 1}};

// Using a 3D vector to represent the grid over time
using GridType = std::vector<std::vector<std::vector<int>>>;

// Forward declarations
void initializeGrid(GridType& grid);
void apply_convolution_tbb(const GridType& grid, std::vector<std::vector<int>>& result,
                           const std::vector<std::vector<int>>& kernel, size_t iter);
void simulate(GridType& grid);
void saveResultsToHDF5(const GridType& grid, const std::string& filename = "tree_growth_simulation.h5");
void setup_logging();

/**
 * @brief Main function to run the simulation
 */
int main() {
  // Initialize the logger
  setup_logging();
  spdlog::info("Starting simulation...");

  // Initialize the grid
  spdlog::info("Initializing grid...");
  GridType grid(iterations + 1, std::vector<std::vector<int>>(height, std::vector<int>(width, 0)));
  initializeGrid(grid);

  // Run the simulation
  spdlog::info("Running simulation...");
  simulate(grid);

  // Save results
  spdlog::info("Saving results...");
  saveResultsToHDF5(grid);

  spdlog::info("Simulation completed successfully!");
  return 0;
}

/**
 * @brief Initialize the grid with random values
 *
 * @param grid The grid to be initialized
 */
void initializeGrid(GridType& grid) {
  // Random number engine
  std::random_device rd;   // Seed for the random number engine
  std::mt19937 gen(rd());  // Standard mersenne_twister_engine seeded with rd()
  std::uniform_int_distribution<> distrib(0, ntree);

  // Set all cells to zero initially
  for (auto& slice : grid) {
    for (auto& row : slice) {
      std::fill(row.begin(), row.end(), 0);
    }
  }

  // Randomize the grid with values from 0 to ntree
  for (auto& row : grid[0]) {
    for (auto& cell : row) {
      cell = distrib(gen);
    }
  }

  // Place a central tree
  size_t central_x = height / 2;
  size_t central_y = width / 2;
  grid[0][central_x][central_y] = 1;  // Placing a young tree at the center
}

/**
 * @brief Apply convolution to the grid using TBB
 *
 * @param grid The grid to apply convolution to
 * @param result The grid to store the result
 * @param kernel The convolution kernel
 * @param iter The iteration number
 */
void apply_convolution_tbb(const GridType& grid, std::vector<std::vector<int>>& result,
                           const std::vector<std::vector<int>>& kernel, size_t iter) {
  int kernel_height = kernel.size();
  int kernel_width = kernel[0].size();
  int kernel_y_offset = kernel_height / 2;
  int kernel_x_offset = kernel_width / 2;

  size_t height = grid[iter].size();
  size_t width = grid[iter][0].size();

  tbb::parallel_for(size_t(0), height, [&](size_t i) {
    for (size_t j = 0; j < width; ++j) {
      int sum = 0;
      for (int k = 0; k < kernel_height; ++k) {
        for (int l = 0; l < kernel_width; ++l) {
          int ni = i + k - kernel_y_offset;
          int nj = j + l - kernel_x_offset;
          if (ni >= 0 && size_t(ni) < height && nj >= 0 && size_t(nj) < width) {
            sum += grid[iter][ni][nj] * kernel[k][l];
          }
        }
      }
      result[i][j] = sum;
    }
  });
}

/**
 * @brief Simulate the growth and reproduction of trees
 *
 * @param grid The grid to simulate
 */
void simulate(GridType& grid) {
  size_t height = grid[0].size();
  size_t width = grid[0][0].size();

  // Temp grid for convolution results
  std::vector<std::vector<int>> N5(height, std::vector<int>(width, 0));
  std::vector<std::vector<int>> R5(height, std::vector<int>(width, 0));

  // Random generator for growth and reproduction probabilities
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> dis(0.0, 1.0);

  for (size_t iter = 0; iter < iterations; ++iter) {
    // Apply convolution to calculate N5 and R5
    apply_convolution_tbb(grid, N5, growth_neighborhood, iter);
    apply_convolution_tbb(grid, R5, reprod_neighborhood, iter);

    // Prepare the next state of the grid
    std::vector<std::vector<int>> new_state(height, std::vector<int>(width, 0));

    // Update states based on N5 and R5
    tbb::parallel_for(size_t(0), height, [&](size_t i) {
      for (size_t j = 0; j < width; ++j) {
        int& cell = grid[iter][i][j];
        int& new_cell = new_state[i][j];
        double random_chance = dis(gen);

        // Growth logic
        if (static_cast<size_t>(cell) > 0 && static_cast<size_t>(cell) < ntree) {
          if (random_chance < grow_prob && N5[i][j] < 1) {
            new_cell = cell + 1;  // grow to next stage
          } else {
            new_cell = cell;  // remain at current stage
          }
        }
        // Reproduction logic
        else if (cell == 0) {
          if (random_chance < reprod_prob * (R5[i][j] / 48.0)) {
            new_cell = 1;  // new tree born
          }
        }
        // Mortality logic
        else if (static_cast<size_t>(cell) == ntree) {
          if (random_chance < mort_prob) {
            new_cell = 0;  // tree dies
          } else {
            new_cell = cell;  // remains at maximum growth
          }
        }
      }
    });

    // Update grid for next iteration
    grid[iter + 1] = new_state;
  }
}

/**
 * @brief Save the results to an HDF5 file
 *
 * @param grid The grid to save
 * @param filename The filename to save the results to
 */
void saveResultsToHDF5(const GridType& grid, const std::string& filename) {
  try {
    // Create a new file using the default property lists.
    H5::H5File file(filename, H5F_ACC_TRUNC);

    // Retrieve dimensions of the grid
    hsize_t dims[3] = {grid.size(), grid[0].size(), grid[0][0].size()};

    // Flatten the grid data for HDF5 writing
    std::vector<int> flat_grid;
    flat_grid.reserve(dims[0] * dims[1] * dims[2]);  // reserve enough space to avoid reallocations
    for (const auto& plane : grid) {
      for (const auto& row : plane) {
        flat_grid.insert(flat_grid.end(), row.begin(), row.end());
      }
    }

    // Create the data space for the dataset.
    H5::DataSpace dataspace(3, dims);

    // Define datatype for the data in the file.
    H5::IntType datatype(H5::PredType::NATIVE_INT);
    datatype.setOrder(H5T_ORDER_LE);

    // Create a dataset creation property list
    H5::DSetCreatPropList prop_list;
    prop_list.setDeflate(6); // Sets the compression level. Here, '6' is a good trade-off between speed and compression efficiency.

    // Define chunk dimensions, typically smaller portions of the dataset dimensions.
    hsize_t chunk_dims[3] = {1, grid[0].size(), grid[0][0].size()}; // Chunking strategy
    prop_list.setChunk(3, chunk_dims); // Apply chunking

    // Create a new dataset within the file using defined dataspace and datatype.
    H5::DataSet dataset = file.createDataSet("TreeGrowthData", datatype, dataspace, prop_list);

    // Write the flattened data to the dataset.
    dataset.write(flat_grid.data(), H5::PredType::NATIVE_INT);

    // Close the dataset and file.
    dataset.close();
    file.close();

    spdlog::info("HDF5 data saved successfully to {}", filename);
  } catch (H5::FileIException& error) {
    spdlog::error("Error: HDF5 File Exception!");
    error.printErrorStack();
  } catch (H5::DataSetIException& error) {
    spdlog::error("Error: HDF5 DataSet Exception!");
    error.printErrorStack();
  } catch (H5::DataSpaceIException& error) {
    spdlog::error("Error: HDF5 DataSpace Exception!");
    error.printErrorStack();
  }
}

/**
 * @brief Setup logging for the application
 */
void setup_logging() {
  // Create color console sink
  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();

  // Create file sink
  auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>("logs/tree_growth_simulation.log", true);

  // Combine both sinks into a single logger
  spdlog::logger logger("multi_sink", {console_sink, file_sink});

  // Set the pattern for both console and file
  // Example pattern: [timestamp] [log level] log message
  logger.set_pattern("[%Y-%m-%d %H:%M:%S] [%^%L%$] %v");

  // Set log level. E.g., debug, info, warn, error
  logger.set_level(spdlog::level::info);

  // Register logger to spdlog
  spdlog::register_logger(std::make_shared<spdlog::logger>(logger));

  // Set as default logger so you can use spdlog::info, spdlog::error, etc.
  spdlog::set_default_logger(std::make_shared<spdlog::logger>(logger));
}
