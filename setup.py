import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iahr", # Replace with your own username
    version="0.0.1",
    author="Nikolay Fedurko",
    author_email="kolausf@gmail.com",
    description="Telegram command execution and event handling framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B1Z0N/iahr",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.2',
)

