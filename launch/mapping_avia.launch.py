import os.path
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command, TextSubstitution
from launch.conditions import IfCondition
def generate_launch_description():
    package_path = get_package_share_directory('fast_livo')
    default_config_path = os.path.join(package_path, 'config')
    executable_binary = os.path.join(package_path.replace('share', 'lib'), 'fastlivo_mapping')

    declare_rviz_cmd = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz'
    )

    fast_livo_node = Node(
        package='fast_livo',
        executable='fastlivo_mapping',
        name='laserMapping',
        output='screen',
        parameters=[{
            'config': PathJoinSubstitution([
                default_config_path,
                'camera_pinhole_resize.yaml'
            ])
        }]
    )
    # fast_livo_node = ExecuteProcess(
    #     cmd=[
    #         'gdb', '--args',
    #         Command([
    #             executable_binary, ' ',
    #             'config:=', PathJoinSubstitution([default_config_path, 'camera_pinhole_resize.yaml'])
    #         ])
    #     ],
    #     output='screen',
    #     shell=True
    # )
    
    rviz_node = Node(
                package='rviz2',
                executable='rviz2',
                name='rviz',
                arguments=['-d', PathJoinSubstitution([
                    package_path, 
                    'rviz_cfg', 
                    'loam_livox.rviz'
                ])],
                condition=IfCondition(LaunchConfiguration('rviz'))
    )

    republish_node = Node(
        package='image_transport',
        executable='republish',
        name='republish',
        arguments=['compressed', 'in:=/left_camera/image', 'raw', 'out:=/left_camera/image'],
        output='screen',
        respawn=True,
    )

    ld = LaunchDescription()
    ld.add_action(declare_rviz_cmd)
    ld.add_action(fast_livo_node)
    # ld.add_action(rviz_node)
    ld.add_action(republish_node)

    return ld