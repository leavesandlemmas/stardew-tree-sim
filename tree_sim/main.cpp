#include <H5Cpp.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <tbb/tbb.h>

#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <nlohmann/json.hpp>
#include <random>
#include <vector>

#include "spdlog/spdlog.h"

using json = nlohmann::json;

struct SimulationConfig {
  size_t ntree = 5;
  size_t num = 120;
  size_t iterations = 100;
  size_t width = 480;   // Default as 4 * num
  size_t height = 360;  // Default as 3 * num
  double reprod_prob = 0.15;
  double grow_prob = 0.2;
  double mort_prob = 0.01;
};

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
void loadConfigFromFile(const std::string& filename, SimulationConfig& config);
void initializeGrid(GridType& grid, const SimulationConfig& config);
void apply_convolution_tbb(const GridType& grid, std::vector<std::vector<int>>& result,
                           const std::vector<std::vector<int>>& kernel, size_t iter);
void simulate(GridType& grid, const SimulationConfig& config);
void saveResultsToHDF5(const GridType& grid, const std::string& filename = "tree_growth_simulation.h5");
void setup_logging();

/**
 * @brief Main function to run the simulation
 */
int main(int argc, char* argv[]) {
  // Initialize the logger
  setup_logging();
  spdlog::info("Starting simulation...");

  SimulationConfig config;  // Default values initialized

  if (argc > 1) {
    std::string configFile = argv[1];
    if (std::filesystem::exists(configFile)) {
      loadConfigFromFile(configFile, config);
      spdlog::info("Configuration loaded from file: {}", configFile);
    } else {
      spdlog::error("Configuration file does not exist: {}", configFile);
      return 1;  // Exit with an error code
    }
  } else {
    spdlog::warn("No configuration file provided. Using default settings.");
  }

  // Initialize the grid
  spdlog::info("Initializing grid...");
  GridType grid(config.iterations + 1, std::vector<std::vector<int>>(config.height, std::vector<int>(config.width, 0)));
  initializeGrid(grid, config);

  // Run the simulation
  spdlog::info("Running simulation...");
  simulate(grid, config);

  // Save results
  spdlog::info("Saving results...");
  saveResultsToHDF5(grid);

  spdlog::info("Simulation completed successfully!");
  return 0;
}

/**
 * @brief Load the simulation configuration from a JSON file
 *
 * @param filename The filename to load the configuration from
 * @param config The configuration object to store the loaded values
 */
void loadConfigFromFile(const std::string& filename, SimulationConfig& config) {
  try {
    std::ifstream file(filename);
    nlohmann::json json;
    file >> json;

    // Only override config if the key exists in the JSON file
    if (json.contains("ntree")) config.ntree = json["ntree"].get<size_t>();
    if (json.contains("num")) config.num = json["num"].get<size_t>();
    if (json.contains("iterations")) config.iterations = json["iterations"].get<size_t>();
    if (json.contains("width")) config.width = json["width"].get<size_t>();
    if (json.contains("height")) config.height = json["height"].get<size_t>();
    if (json.contains("reprod_prob")) config.reprod_prob = json["reprod_prob"].get<double>();
    if (json.contains("grow_prob")) config.grow_prob = json["grow_prob"].get<double>();
    if (json.contains("mort_prob")) config.mort_prob = json["mort_prob"].get<double>();

    spdlog::info("Configuration loaded from file: {}", filename);
  } catch (const std::exception& e) {
    spdlog::error("Error reading configuration: {}", e.what());
    // exiting on error
    exit(1);
  }
}

/**
 * @brief Initialize the grid with random values
 *
 * @param grid The grid to be initialized
 * @param config The configuration object to use for initialization
 */
void initializeGrid(GridType& grid, const SimulationConfig& config) {
  // Random number engine
  std::random_device rd;   // Seed for the random number engine
  std::mt19937 gen(rd());  // Standard mersenne_twister_engine seeded with rd()
  std::uniform_int_distribution<> distrib(0, config.ntree);

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
  size_t central_x = config.height / 2;
  size_t central_y = config.width / 2;
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
 * @param config The configuration object to use for simulation
 */
void simulate(GridType& grid, const SimulationConfig& config) {
  size_t height = config.height;
  size_t width = config.width;

  // Temp grid for convolution results
  std::vector<std::vector<int>> N5(height, std::vector<int>(width, 0));
  std::vector<std::vector<int>> R5(height, std::vector<int>(width, 0));

  // Random generator for growth and reproduction probabilities
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<> dis(0.0, 1.0);

  for (size_t iter = 0; iter < config.iterations; ++iter) {
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
        if (static_cast<size_t>(cell) > 0 && static_cast<size_t>(cell) < config.ntree) {
          if (random_chance < config.grow_prob && N5[i][j] < 1) {
            new_cell = cell + 1;  // grow to next stage
          } else {
            new_cell = cell;  // remain at current stage
          }
        }
        // Reproduction logic
        else if (cell == 0) {
          if (random_chance < config.reprod_prob * (R5[i][j] / 48.0)) {
            new_cell = 1;  // new tree born
          }
        }
        // Mortality logic
        else if (static_cast<size_t>(cell) == config.ntree) {
          if (random_chance < config.mort_prob) {
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
    prop_list.setDeflate(6);  // Sets compression level to '6'

    // Define chunk dimensions, typically smaller portions of the dataset dimensions.
    hsize_t chunk_dims[3] = {1, grid[0].size(), grid[0][0].size()};  // Chunking strategy
    prop_list.setChunk(3, chunk_dims);                               // Apply chunking

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
