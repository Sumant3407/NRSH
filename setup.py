
from setuptools import setup, find_packages
from pathlib import Path

readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="road-safety-analysis",
    version="1.0.0",
    description="AI-powered road infrastructure analysis system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Road Safety Hackathon Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-multipart>=0.0.6",
        "pydantic>=2.5.0",
        "torch>=2.1.0",
        "torchvision>=0.16.0",
        "ultralytics>=8.1.0",
        "opencv-python>=4.8.1",
        "numpy>=1.24.3",
        "Pillow>=10.1.0",
        "scikit-learn>=1.3.2",
        "geopy>=2.4.1",
        "pandas>=2.1.3",
        "reportlab>=4.0.7",
        "pyyaml>=6.0.1",
        "aiofiles>=23.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)