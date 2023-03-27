import pathlib

from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="marketwatch",
    version="0.1.2",
    description="MarketWatch's API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/antoinebou12/marketwatch",
    author="antoinebou12",
    author_email="antoine.boucher.1@etsmtl.ca",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["marketwatch"],
    include_package_data=True,
    install_requires=["beautifulsoup4", "requests"],
)
