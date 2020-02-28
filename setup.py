from distutils.core import setup
setup(
  name = 'cerberus',
  packages = ['cerberus'],
  version = '0.1',
  license='MIT',
  description = 'Lightweight asynchronous web framework',
  author = 'Khant',
  author_email = 'contact@khant.dev',
  url = 'https://github.com/the-robot/cerberus',
  download_url = 'https://github.com/the-robot/cerberus/archive/v_01.tar.gz',
  keywords = ['Asynchronous', 'Web framework'],
  install_requires=[
    "aiofiles",
    "Jinja2",
    "parse",
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)