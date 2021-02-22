'''
Created on 8-Oct-2020

@author: M. Fortin and R. Saint-Amant, Canadian Forest Service, August 2020
@copyright: Her Majesty the Queen in right of Canada
'''
from setuptools import find_packages
from setuptools import setup

setup(
    name="biosim",
    version="1.0.6",
    url="https://sourceforge.net/p/mrnfforesttools/biosimclient/wiki/MainPage/",
    license="LGPL 3.0",
    maintainer="Mathieu Fortin",
    maintainer_email="mathieu.fortin.re@gmail.com",
    description="A web service for climate variables and pest development stages.",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask", "waitress", "itsdangerous", "jinja2", "markupsafe", "six", "werkzeug", "paste"],
)