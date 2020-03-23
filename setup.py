from distutils.core import setup
setup(
  name = 'yaas',
  packages = ['yaas', 'yaas.middleware'],
  version = '0.1.5',
  license='LGPL',
  description = 'Lightweight asynchronous web framework',
  author = 'Khant',
  author_email = 'contact@khant.dev',
  url = 'https://github.com/yaas-project/yaas',
  download_url = 'https://github.com/yaas-project/yaas/releases/download/v0.1.5/yaas-0.1.5.tar.gz',
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
