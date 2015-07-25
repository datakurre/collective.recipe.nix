from setuptools import setup, find_packages

setup(
    name='collective.recipe.nix',
    version='0.18.0',
    description="Buildout recipe for creating Nix expressions from eggs list",
    long_description=(open('README.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Buildout :: Recipe',
        'Framework :: Buildout',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
    ],
    keywords='',
    author='Asko Soukka',
    author_email='asko.soukka@iki.fi',
    url='https://github.com/datakurre/collective.recipe.nix/',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    namespace_packages=['collective', 'collective.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.recipe.egg',
        'future',
    ],
    extras_require={'test': [
    ]},
    entry_points="""
    # -*- Entry points: -*-
    [zc.buildout]
    default = collective.recipe.nix:Nix
    """
)
