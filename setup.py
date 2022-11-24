from setuptools import find_packages , setup

with open("requirements.txt",encoding="utf-8",mode="r+") as f:
    requirements = [requires.strip() for requires in f.readlines()]

setup(
    name="oceans",
    description="Webscraping live ocean webcams",
    author="Channi",
    version="0.1",
    packages = find_packages(),
    install_requires=requirements
)
