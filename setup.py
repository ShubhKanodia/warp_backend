from setuptools import setup, find_packages

setup(
    name="agentswarm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "langchain==0.1.9",
        "openai==1.12.0",
        "sqlalchemy==2.0.27",
        "pytest==8.0.2",
        "pydantic==2.6.1",
        "python-dotenv==1.0.1",
        "python-multipart==0.0.9",
        "aiohttp==3.9.3"
    ],
    python_requires=">=3.8",
    author="Shubh",
    author_email="your.email@example.com",
    description="A multi-agent system built with FastAPI and LangChain",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentswarm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 