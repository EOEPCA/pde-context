from setuptools import setup, find_packages

packagename="pdecontext"

#with open('requirements.txt') as f:
#    required = f.read().splitlines()

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points='''
        [console_scripts]
        pde-context=pdecontext.main:cli
    '''.format(packagename=packagename),
)