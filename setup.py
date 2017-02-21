from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('ooc/__init__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setup(
    name='ooc',
    version=main_ns['__version__'],
    description='AE4441-16 Operations Optimization assignment',
    author='Aaron de Windt, Kyana Shayan',
    author_email='aaron.dewindt@gmail.com, kyana.shayan@gmail.com',

    install_requires=['numpy', 'scipy', 'lxml', 'recordclass'],
    packages=find_packages('.', exclude=["test"]),

    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 2 - Pre-Alpha'],
)
