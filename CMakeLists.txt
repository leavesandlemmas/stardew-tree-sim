cmake_minimum_required(VERSION 3.15)

# Project Name
project(TreeGrowthSimulation)

# Set C++ standard to C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Find required packages
find_package(TBB CONFIG REQUIRED)
find_package(HDF5 REQUIRED COMPONENTS CXX)
find_package(spdlog REQUIRED)

# Include directories for HDF5
include_directories(${HDF5_INCLUDE_DIRS})

# Include directories from CONDA environment
link_directories(
    $ENV{CONDA_PREFIX}/lib
)

# Add compiler flags
add_compile_options(
  -O3
  -std=c++20
  -march=native
  -ffast-math
  -pthread
  -Wall
  -Wextra
)

# Add executable
add_executable(TreeGrowthSim tree_sim/main.cpp)

# Link libraries
target_link_libraries(
    TreeGrowthSim
    PRIVATE
    TBB::tbb
    spdlog::spdlog
    ${HDF5_LIBRARIES}
)
