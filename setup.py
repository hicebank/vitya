import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='vitya',
    version='0.20.19',
    author='hicebank.ru',
    author_email='inyutin@hicebank.ru',
    description='Validators for different russian banking values',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hicebank/vitya',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    package_data={
        "vitya": ["py.typed"],
    },
)
