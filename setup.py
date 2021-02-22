from setuptools import find_packages, setup

setup(
    name='iped_jobs',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "Werkzeug==0.16.1",
        "flask_restplus",
        "docopt",
        "requests",
        "kubernetes"
    ],
)
