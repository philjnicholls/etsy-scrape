import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

    setuptools.setup(
        name='scrape_etsy',
        version='0.0.1',
        author='Phil Nicholls',
        author_email='phil.j.nicholls@gmail.com',
        description='Scrapes data from Etsy search results',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/philjnicholls/etsy-scrape',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
        ],
        python_requires='>=3.6',
        install_requires=[
            'beautifulsoup4',
            'requests',
            'pymemcache',
        ]
    )
