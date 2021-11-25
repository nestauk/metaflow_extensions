from setuptools import find_namespace_packages
from setuptools import setup


REQUIRES = ["metaflow>=2.5.4"]

setup(
    name="metaflow_extensions",
    install_requires=REQUIRES,
    python_requires=">=3.7",
    packages=find_namespace_packages(include=["metaflow_extensions.*"]),
    version="0.3.0",
    description="Nesta plugins for Metaflow (metaflow.org)",
    author="Nesta",
    license="MIT",
)
