from setuptools import setup, find_packages

setup(
    name="ai_engine",
    version="0.1.0",
    packages=["ai_engine"] + ["ai_engine." + p for p in find_packages(exclude=["tests*"])],
    package_dir={"ai_engine": "."},
)
