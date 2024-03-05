from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="routingfilter",
    version="2.2.7",
    packages=find_packages(include=["routingfilter", "routingfilter.*"]),
    include_package_data=True,
    install_requires=["IPy~=1.1", "macaddress~=2.0.2"],
    url="https://github.com/certego/RoutingFilter",
    license="GNU LGPLv3",
    author="Certego S.r.l.",
    author_email="support@certego.net",
    description="Generic Business Logic Implementation for Routing objects as python dictionaries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)
