cmake_minimum_required(VERSION 3.8)
project(fast_livo)
set(CMAKE_BUILD_TYPE Debug)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_compile_options(-std=c++14 -O3 -fexceptions)

add_definitions(-DROOT_DIR=\"${CMAKE_CURRENT_SOURCE_DIR}/\")

message("Current CPU architecture: ${CMAKE_SYSTEM_PROCESSOR}")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "(x86)|(X86)|(amd64)|(AMD64)")
  include(ProcessorCount)
  ProcessorCount(N)
  message("Processor number:  ${N}")
  if(N GREATER 5)
    add_definitions(-DMP_EN -DMP_PROC_NUM=4)
    message("Core for MP:  4")
  elseif(N GREATER 3)
    math(EXPR PROC_NUM "${N} - 2")
    add_definitions(-DMP_EN -DMP_PROC_NUM=${PROC_NUM})
    message("Core for MP:  ${PROC_NUM}")
  else()
    add_definitions(-DMP_PROC_NUM=1)
  endif()
else()
  add_definitions(-DMP_PROC_NUM=1)
endif()

find_package(OpenMP QUIET)
if(OPENMP_FOUND)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

find_package(PythonLibs REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(tf2_geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_eigen REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(image_transport REQUIRED)
find_package(pcl_conversions REQUIRED)

find_package(livox_ros_driver2 REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(PCL REQUIRED)
find_package(OpenCV REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread)

list(APPEND CMAKE_PREFIX_PATH "$ENV{HOME}/ros2_ws/src/Sophus/install/lib")
set(Sophus_INCLUDE_DIR "$ENV{HOME}/ros2_ws/src/Sophus/install/include")
find_package(Sophus REQUIRED)
find_package(vikit_ros2 REQUIRED)

set(vio_dependencies
  rclcpp
  sensor_msgs
  std_msgs
  geometry_msgs
  cv_bridge
  image_transport
  nav_msgs
  tf2_ros
  tf2_eigen
  vikit_ros2
)
set(livo_dependencies
  ${vio_dependencies}
  visualization_msgs
  rclcpp_components
  nav_msgs
  pcl_conversions
  tf2
  cv_bridge
  livox_ros_driver2
)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Pose6D.msg"
  "msg/States.msg"
  DEPENDENCIES std_msgs geometry_msgs
)
ament_export_dependencies(rosidl_default_runtime)

include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
  ${PCL_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS}
  ${OpenCV_INCLUDE_DIRS}
)
add_library(ikdtree
  include/ikd-Tree/ikd_Tree.cpp
  include/FOV_Checker/FOV_Checker.cpp
)
target_include_directories(ikdtree PUBLIC
  ${Sophus_INCLUDE_DIR}
)
message("Sophus_INCLUDE_DIR: ${Sophus_INCLUDE_DIR}")
message("Sophus_LIBRARIES: ${Sophus_LIBRARIES}")
message("vikit_common_INCLUDE_DIRS: ${vikit_common_INCLUDE_DIRS}")
message("vikit_common_LIBRARIES: ${vikit_common_LIBRARIES}")
add_library(vio
  src/lidar_selection.cpp
  src/frame.cpp
  src/point.cpp
  src/map.cpp
)
target_include_directories(vio PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_cpp>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
  ${Sophus_INCLUDE_DIR}
)
add_executable(fastlivo_mapping
  src/laserMapping.cpp
  src/IMU_Processing.cpp
  src/preprocess.cpp
)
target_include_directories(fastlivo_mapping PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_cpp>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(fastlivo_mapping
  ${PCL_LIBRARIES}
  ${PYTHON_LIBRARIES}
  vio
  ikdtree
)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(fastlivo_mapping ${cpp_typesupport_target})
target_link_libraries(vio ${cpp_typesupport_target})

ament_target_dependencies(vio ${vio_dependencies})
ament_target_dependencies(fastlivo_mapping ${livo_dependencies})

install(TARGETS fastlivo_mapping vio ikdtree 
  DESTINATION lib/${PROJECT_NAME}
)
install(FILES ${Sophus_LIBRARIES}  ${vikit_common_LIBRARIES}
  DESTINATION lib/${PROJECT_NAME}
)
install(DIRECTORY config launch rviz_cfg
  DESTINATION share/${PROJECT_NAME}
)
ament_package()