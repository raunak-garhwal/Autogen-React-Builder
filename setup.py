from setuptools import setup, find_packages

setup(
    name="autogen-react-builder",
    version="1.0.0",
    packages=find_packages(include=["backend", "backend.*"]),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "autogen",
        "pydantic",
    ],
) 