from typing import List
from setuptools import find_packages,setup

def get_requirements() -> List[str]:
    """
    returns the list of package requirements from the requirements file
    """
    require_list:List[str] = []
    with open("requirements.txt","r") as requirements:
        lines = requirements.readlines()
        for l in lines:
            require_list.append(l.replace("\n",""))
    return require_list

setup (
    name="sensor",
    version="1.0",
    author="Srinidhi Karjol",
    author_email="srinidhikarjol@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)
