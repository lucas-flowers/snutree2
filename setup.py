
from pathlib import Path
from setuptools import setup, find_packages

DIR = Path(__file__).parent
with (DIR/'README.txt').open('r') as f:
    long_description = f.read()

setup(

        name='snutree',
        use_scm_version=True,
        setup_requires=['setuptools_scm'],
        description='Visualize big–little brother/sister relationships in Greek-letter organizations',
        long_description=long_description,
        url='https://github.com/lucas-flowers/snutree',
        author='Lucas Flowers',
        author_email='laf62@case.edu',
        license='GPLv3',

        classifiers = [
            'Development Status :: 4 - Beta',
            'Intended Audience :: Other Audience',
            'Topic :: Other/Nonlisted Topic',
            'Topic :: Utilities',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Programming Language :: Python :: 3.5',
            ],

        keywords='big little brother sister family tree',
        packages=find_packages(exclude=['tests']),

        install_requires=[
            'Cerberus',
            'click',
            'networkx',
            'pluginbase',
            'PyYAML',
            'voluptuous',
            ],

        python_requires='>=3.5',

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

