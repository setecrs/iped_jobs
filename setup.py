from setuptools import find_packages, setup

setup(
    name='sardadmin',
    version='2.5.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "Werkzeug==0.16.1",
        "flask_restplus",
        "docopt",
        "requests",
        "ldap3",
        "kubernetes",
        "prometheus_client",
        "pyfakefs",
        "PyJWT"
    ],
)
