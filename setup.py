from setuptools import setup, find_packages

packagename="pde-context"

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name=packagename,
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    entry_points='''
        [console_scripts]
        {packagename}=pdecontext.main:cli
    '''.format(packagename=packagename),
)