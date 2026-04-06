from setuptools import find_packages, setup

package_name = 'assem1_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mohamed',
    description='Vision package',
    license='MIT',
    entry_points={
        'console_scripts': [
            'color_detector = assem1_vision.color_detector:main',
        ],
    },
)