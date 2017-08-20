
from pathlib import Path
from setuptools import setup, find_packages

with (Path(__file__).parent/'README.txt').open('r') as f:
    long_description = f.read()

setup(

        name='snutree',
        version='0.1.1',
        descripton='Big—Little Tree',
        long_description=long_description,
        url='', # TODO
        author='Lucas Flowers',
        author_email='laf62@case.edu',
        license='GPLv3',

        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Other Audience',
            'Topic :: Other/Nonlisted Topic',
            'Topic :: Sociology :: Genealogy',
            'Topic :: Sociology :: History',
            'Topic :: Utilities',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.6',
            ],

        keywords='big little brother sister family tree',
        packages=find_packages(exclude=['tests', 'private']),

        install_requires=[
            'Cerberus',
            'click',
            'networkx',
            'pluginbase',
            'PyYAML',
            'voluptuous',
            ],

        python_requires='>=3.6',

        extras_require={
            'test' : ['pytest'],
            'qt' : ['PyQt5'],
            'read_sql' : ['mysqlclient'],
            'read_sql_ssh' : ['mysqlclient', 'sshtunnel'],
            'read_dot' : ['pydotplus']
            },

        package_data={
            '' : ['*.txt'],
            'snutree' : ['readers/*.py', 'schemas/*.py', 'writers/*.py'],
            },

        entry_points={
            'console_scripts' : [
                'snutree=snutree.cli:main',
                'snutree-qt=snutree.qt:main',
                ]
            }

        )




