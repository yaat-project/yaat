from distutils.core import setup
setup(
  name = 'yaat',
  packages = ['yaat', 'yaat.middleware'],
  version = '0.1.0',
  license='LGPL',
  description = 'Yet another ASGI toolkit',
  author = 'Khant',
  author_email = 'contact@khant.dev',
  url = 'https://github.com/yaat-project/yaat',
  download_url = 'https://github.com/yaat-project/yaat/releases/download/v0.1.0/yaat-0.1.0.tar.gz',
  keywords = ['Asynchronous', 'Web framework'],
  install_requires=[
    "Jinja2",
    "aiofiles",
    "httpx",
    "parse",
    "python-multipart",
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
