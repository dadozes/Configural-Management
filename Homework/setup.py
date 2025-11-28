from setuptools import setup, find_packages

setup(
    name="config-parser",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "config-parser=config_parser.main:main",
        ],
    },
    python_requires=">=3.7",
)
