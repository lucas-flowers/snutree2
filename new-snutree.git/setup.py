
from setuptools import setup, find_packages

setup(

    name='snutree',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description='Visualize big–little brother/sister relationships in Greek-letter organizations',
    url='https://github.com/lucas-flowers/snutree',
    author='Lucas Flowers',
    author_email='laf62@case.edu',
    license='GPLv3',

    # TODO Copy in setup stuff from old snutree

    packages=find_packages(exclude=['tests']),

)

