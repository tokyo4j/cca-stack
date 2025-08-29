cmake_minimum_required(VERSION 4.0)
project(llama-test CXX)

set(LLAMA_CURL OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

set(BUILD_SHARED_LIBS OFF CACHE BOOL " " FORCE)
set(CMAKE_FIND_LIBRARY_SUFFIXES ".a")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static")

set(LLAMA_CPP_DIR "${CMAKE_SOURCE_DIR}/../llama.cpp")
add_subdirectory(${LLAMA_CPP_DIR} llama.cpp)
add_executable(llama-test llama-test.cpp)
target_include_directories(llama-test PRIVATE ${LLAMA_CPP_DIR})
target_link_libraries(llama-test PRIVATE llama)
