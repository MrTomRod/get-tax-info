# based on https://realpython.com/pypi-publish-python-package
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
    name='get-tax-info',
    version='0.0.1',
    description='Convert NCBI TaxIDs to scientific species names and vice-versa',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/MrTomRod/get-tax-info',
    author='Thomas Roder',
    author_email='roder.thomas@gmail.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    packages=['get_tax_info'],
    include_package_data=True,  # see MANIFEST.in
    install_requires=[],  # pandas is only needed to add columns to csv
    entry_points={
        'console_scripts': [
            'get-tax-info=get_tax_info.cli:main',
        ]
    },
)
