from setuptools import setup, find_packages
from codecs import open
from os import path


#   TODO see https://packaging.python.org/tutorials/distributing-packages/

thisDirectory = path.abspath(path.dirname(__file__))

with open(path.join(thisDirectory, "README.rst"), encoding="utf-8") as f:
    fullDescription = f.read()
    f.close()

setup(
    name="RoverBot",
    packages=["RoverBot"],
    version="1.0.0.dev1",
    description="A simple robot package.",
    long_description=fullDescription,
    author="Timothy Darrah",
    author_email="timothy.s.darrah@vanderbilt.edu",
    license="MIT",
    url="https://github.com/darrahts/TeachableRobots",
    download_url="https://github.com/darrahts/TeachableRobots.git",
    keywords=["robot", "rover", "roverbot", "arduino"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Robotics",
        "License :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        ]
    packages=find_packages(),
    install_requires=[], #   TODO here https://wheel.readthedocs.io/en/stable/ for example
    extras_require={}, #   TODO here https://wheel.readthedocs.io/en/stable/ for example
    package_data={}, #   TODO here
    entry_points={}, #   TODO here
    )
