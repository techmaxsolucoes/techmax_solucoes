from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in techmax_solucoes/__init__.py
from techmax_solucoes import __version__ as version

setup(
	name="techmax_solucoes",
	version=version,
	description="WebSite da TechMax",
	author="TechMax Soluções",
	author_email="info@techmaxsolucoes.com.br",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
