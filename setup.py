#!/usr/bin/env python

from setuptools import setup, find_packages

from fotopruvodce import __version__ as VERSION


setup(
    name='fotopruvodce',
    version=VERSION,
    author='Jan Seifert',
    author_email='jan.seifert@fotkyzcest.net',
    description=(
        'Fotografická diskusní aplikace poskytujici prostor fotografům '
        'libovolného ražení k diskusi svých problémů, či sdělování '
        'zkušenosti.'
    ),
    license='BSD',
    platforms=['any'],
    url='https://github.com/seifert/fotopruvodce',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Natural Language :: Czech',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.11,<1.12',
        'html2text',
        'markdown',
        'Pillow',
        'sqlparse',
    ],
    entry_points={
        'console_scripts': [
            'manage-fotopruvodce = fotopruvodce:main',
        ]
    }
)
