import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='get-stick-bugged-lol',
    version='0.0.1',
    author='n0spaces',
    description="'Get stick bugged' video generator",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/n0spaces/get_stick_bugged_lol',
    packages=setuptools.find_packages(),
    package_data={'gsbl': ['media/*.*']},
    entry_points={'console_scripts': ['gsbl=gsbl.__main__:main']},
    install_requires=['pylsd-nova', 'numpy', 'Pillow', 'moviepy'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
