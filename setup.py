from setuptools import setup, find_packages
import sys, os

version = '0.3dev'

setup(name='django_courseaffils',
      version=version,
      description="course affiliations",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=[
        "http://svn.ccnmtl.columbia.edu/djangohelpers/trunk#egg=djangohelpers-dev",
        ],
      install_requires=[
        "djangohelpers==dev",
      ],
      entry_points="""
      """,
      )
