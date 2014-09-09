from distutils.core import setup


setup(
    name='bdb',
    version='0.0.1',
    description='Create YASARA scenes from WHAT IF lists.',
    author='Wouter Touw',
    author_email='wouter.touw@radboudumc.nl',
    license="To be decided",
    url='https://github.com/cmbi/scenes',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    packages=[
        'yas_scenes',
        'yas_scenes.tests',
    ],
    scripts=['scripts/scenes'],
)
