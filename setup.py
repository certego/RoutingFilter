from setuptools import setup

setup(
    name='routingfilter',
    version='1.0',
    packages=['routingfilter'],
    include_package_data=True,
    install_requires=["IPy"],
    url='https://github.com/certego/RoutingFilter',
    license='GNU LGPLv3',
    author='Certego S.r.l.',
    author_email='support@certego.net',
    description='Generic Business Logic Implementation for Routing objects as python dictionaries'
)
