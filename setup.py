"""Setup script for the Stock Trading Decision Support System."""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='stock-trading-decision-support',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A machine learning-based stock trading decision support system',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/stock-trading-decision-support',
    packages=find_packages(exclude=['tests', 'tests.*', 'notebooks', 'docker']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.9.0',
            'flake8>=6.1.0',
            'isort>=5.12.0',
            'mypy>=1.5.0',
        ],
        'docs': [
            'Sphinx>=7.2.0',
            'sphinx-rtd-theme>=1.3.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'trade-download-data=scripts.download_historical_data:main',
            'trade-train-models=scripts.train_models:main',
            'trade-backtest=scripts.run_backtest:main',
        ],
    },
    include_package_data=True,
    package_data={
        'src': ['config/*.yaml'],
    },
    zip_safe=False,
    keywords='stock trading machine-learning lstm gru prediction finance',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/stock-trading-decision-support/issues',
        'Source': 'https://github.com/yourusername/stock-trading-decision-support',
        'Documentation': 'https://github.com/yourusername/stock-trading-decision-support/blob/main/README.md',
    },
)
