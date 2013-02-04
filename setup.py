from setuptools import setup, find_packages

version = '0.4.2'


setup(name='django-courseaffils',
      version=version,
      description="course affiliations",
      long_description="",
      classifiers=[],
      keywords='',
      author='CCNMTL',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links=[
        ],
      install_requires=[
        "djangohelpers",
      ],
      entry_points="""
      """,
      )
