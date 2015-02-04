__author__ = 'nevehanter'

from setuptools import setup

setup(
    name="conparser",
    version="0.1",
    description="Multiformat contact parsing library",
    author="Kamil Bar <nevehanter@gmail.com>",
    license="BSD",

    packages=['conparser'],

    install_requires=[
        'chardet'
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)