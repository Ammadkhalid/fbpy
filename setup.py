from setuptools import setup

setup(
    name='fbpy',

    version='0.1',

    author='Ammad Khalid',

    author_email='Ammadkhalid12@gmail.com',

    license='CopyRight',

    url = "http://pypi.python.org/pypi/pyfb",

    long_description=open('README.md').read(),

    packages = ["fbpy", "fbpy/Module"],

    python_requires = '>=3',

    entry_points = {
          'console_scripts': ['fb = fbpy.__main__:main']
        },

    install_requires=[
    'dataset == 1.0.5',
    'facepy == 1.0.9',
    'requests == 2.18.1',
    'retrying == 1.3.3'
    ]

)
