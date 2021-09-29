from setuptools import find_packages
from setuptools import setup


REQUIRES = ["metaflow>=2.3.7"]

setup(
    name="metaflow_extensions",
    install_requires=REQUIRES,
    python_requires=">=3.7",
    packages=find_packages(),
    version="0.1.0",
    description="Nesta plugins for Metaflow (metaflow.org)",
    author="Nesta",
    license="MIT",
)
