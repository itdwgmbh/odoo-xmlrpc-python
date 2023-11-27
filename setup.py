from setuptools import setup, find_packages

setup(
    name='odoo_xmlrpc',
    version='1.0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    author='IT-DW GmbH',
    author_email='support@it-dw.com',
    description='A Python module to interact with Odoo XML-RPC API',
    keywords='odoo xml-rpc api',
    url='https://github.com/itdwgmbh/odoo-xmlrpc-python',
    license='GPLv3'
)