import setuptools

setuptools.setup(
    name='get-stick-bugged-lol',
    version='0.0.1',
    author='n0spaces',
    description="'Get stick bugged' video generator",
    url='https://github.com/n0spaces/get_stick_bugged_lol',
    packages=setuptools.find_packages(),
    package_data={'gsbl': ['media/*.*']},
    entry_points={'console_scripts': ['gsbl=gsbl.main_cli:main']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
