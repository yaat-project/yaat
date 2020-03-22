from distutils.core import setup
setup(
  name = 'nymph',
  packages = ['nymph'],
  version = '0.1.2',
  license='LGPL',
  description = 'Lightweight asynchronous web framework',
  author = 'Khant',
  author_email = 'contact@khant.dev',
  url = 'https://github.com/the-robot/nymph',
  download_url = 'https://github.com/the-robot/nymph/releases/download/v0.1.2/nymph-0.1.2.tar.gz',
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
    'License :: OSI Approved :: LGPL License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
