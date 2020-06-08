from distutils.core import setup
setup(
  name = 'PetriScanner2',
  packages = ['PetriScanner2'],
  version = '0.1',
  license='License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
  description = 'Free open source digital plate reader',
  author = 'Diego Fernandez',
  author_email = 'deg1795@gmail.com',
  url = 'https://github.com/Dfernand1795/PetriScanner2',
  download_url = 'https://github.com/Dfernand1795/PetriScanner2/archive/PetriScanner2_V001.tar.gz',
  keywords = ['Digital', 'Plate', 'Reading', 'Bacteria', 'Growth', 'Image', 'Analysis'],
  package_dir={'': '..'}, 
  install_requires=[
            'pyinsane2',
            'numpy',
            'pandas',
            'seaborn',
            'matplotlib',
            'scipy'],
  classifiers=[
    'Development Status :: 4 - Beta',   
    'Intended Audience :: Science/Research',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)