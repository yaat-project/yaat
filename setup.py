from setuptools import setup

VERSION = "0.1.10"


def get_long_description():
    with open("README.md", encoding="utf8") as f:
        return f.read()


setup(
    name="yaat",
    packages=["yaat", "yaat.middleware", "yaat.openapi"],
    version=VERSION,
    license="LGPL",
    description="Yet another ASGI toolkit",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Khant",
    author_email="contact@khant.dev",
    url="https://github.com/yaat-project/yaat",
    download_url=f"https://github.com/yaat-project/yaat/releases/download/v{VERSION}/yaat-{VERSION}.tar.gz",
    keywords=["asynchronous", "web framework"],
    python_requires=">=3.6",
    install_requires=[
        "aiofiles",
        "httpx",
        "Jinja2",
        "parse",
        "python-multipart",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
