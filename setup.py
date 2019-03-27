from setuptools import setup
import sys

setup(name='py8583',
      version='1.3',
      
      description='ISO8583 python library',
      long_description=open('README.md').read(),
      
      classifiers=[
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Operating System :: OS Independent',
        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        
        'Topic :: Communications',
        'Intended Audience :: Developers',
      ],
      
      keywords='ISO8583 banking protocol library',
      
      url='https://github.com/alxnik/py8583',
      author='Alexandros Nikolopoulos',
      author_email='alxnik@gmail.com',
      
      license='LGPLv2',
      packages=['py8583'],
      install_requires=['enum34'] if sys.version_info < (3,4) else [],
      zip_safe=True)