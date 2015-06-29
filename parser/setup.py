from setuptools import setup

setup(
    name='tablemagician',
    version='0.1',
    packages=['tablemagician'],
    url='',
    license='',
    author='sebastian',
    author_email='',
    description='A simple CSV parser based on messytables',
    long_description=open('README').read(),
    install_requires=['messytables', 'ftfy'],
    entry_points={
        'console_scripts': [
            'tablemagician = tablemagician.main:main'
        ]
    }
)
