from setuptools import setup, find_packages

setup(
    name="phil-cli",
    version="1.0.0",
    author="Your Name",
    description="Client CLI for Phil AI Agent",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        'console_scripts': [
            'phil=phil_cli.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)