from setuptools import setup, find_packages

setup(
    name="xdp",
    version="0.1.0",
    description="A package to process x-ray astrophysical data",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "astroquery",
        "matplotlib",
        "seaborn",
    ],
    author="Philip Rooney",
    author_email="p_rooney@hotmail.com",
    license="MIT",
    url="https://github.com/clustercosmos/xdp",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)