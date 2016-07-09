try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='logreplay',
    version='0.2.0',
    packages=['logreplay'],
    url='https://github.com/jacexh/log-replay',
    license='MIT',
    author='jace',
    author_email='jace@xuh.me',
    description='a log-based tool to replay http requests',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=[
        "aiohttp",
    ]
)
