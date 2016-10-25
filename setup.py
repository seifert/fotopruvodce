#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='fotopruvodce',
    version='0.0.1',
    author='Jan Seifert',
    author_email='jan.seifert@fotkyzcest.net',
    description=(
        'Fotografická diskusní aplikace poskytujici prostor fotografům '
        'libovolného ražení k diskusi svých problémů, či sdělování '
        'zkušenosti.'
    ),
    license='BSD',
    platforms=['any'],
    url='http://fotopruvodce.cz/',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Natural Language :: Czech',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Framework :: Django :: 1.10',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django>=1.10,<1.11',
        'Pillow',
    ],
    entry_points={
        'console_scripts': [
            'manage-fotopruvodce = fotopruvodce:main',
        ]
    }
)
