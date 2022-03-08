from setuptools import setup
import re

version = ''
with open('horsereality/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setup(
    name='horsereality',
    author='shayypy',
    url='https://github.com/hr-tools/horsereality',
    version=version,
    packages=['horsereality'],
    description='Simple client library for reading pages on Horse Reality.',
    install_requires=['aiohttp', 'beautifulsoup4'],
    python_requires='>=3.6'
)
