from setuptools import find_packages
from setuptools import setup


REQUIRES = ["toolz==0.11"]

setup(
    name="myproject",
    install_requires=REQUIRES,
    packages=find_packages(),
    version="0.1.0",
    description="Test project",
    author="pytest",
)

