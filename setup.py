"""
Setup configuration for EthicaLang
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text() if readme_file.exists() else ''

setup(
    name='ethicalang',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='An ethically-aware programming language with static analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ethicalang',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies - pure Python!
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'ethicalang=ethicalang.cli.main:main',
        ],
    },
)
