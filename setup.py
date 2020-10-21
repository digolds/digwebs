import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="digwebs-slz", # Replace with your own username
    version="0.0.5",
    author="SLZ",
    author_email="founders@digolds.cn",
    description="A tiny web framework-digwebs ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/digolds/digwebs",
    entry_points={
        'console_scripts': [
            'digwebs = digwebs.project_generator:gen',
        ],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)