import setuptools

setuptools.setup(
    name='pytest-pep257',
    version='0.0.5',
    description='py.test plugin for pep257',
    author='Anders Emil Nielsen',
    author_email='aemilnielsen@gmail.com',
    long_description=open('README.rst').read(),
    py_modules=['pytest_pep257'],
    install_requires=[
        'pytest>=2.6.0',
        'pep257>=0.3.2'
    ],
    entry_points={'pytest11': ['pytest_pep257 = pytest_pep257']},
    license='MIT License'
)
