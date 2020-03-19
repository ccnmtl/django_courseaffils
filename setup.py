from setuptools import setup, find_packages

version = '2.2.3'


setup(
    name='django-courseaffils',
    version=version,
    description="course affiliations",
    long_description="a django app which manages course information",
    classifiers=[],
    keywords='',
    author='Columbia University\'s Center for Teaching and Learning',
    author_email='ctl-dev@columbia.edu',
    url='https://github.com/ccnmtl/django_courseaffils/',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Django",
    ],
    entry_points="""
      """,
)
