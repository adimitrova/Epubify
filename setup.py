import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    nname = "ani.dimitrova",
    version="0.0.1",
    author="Anelia Dimitrova",
    author_email="a.dimitrovaa@gmail.com",
    description="Pocket to Epub converter",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/adimitrova/Epubify/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix-based",
    ],
    package_dir={"": "epubify"},
    packages=setuptools.find_packages(where="epubify"),
    python_requires=">=3.6",
)