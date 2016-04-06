try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='logreplay',
    version=open('version', 'r').read().strip(),
    packages=['logreplay'],
    url='',
    license='MIT',
    author='jace',
    author_email='jace@xuh.me',
    description='a common log replay tool',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[
        "aiohttp",
        "janus"
    ]
)