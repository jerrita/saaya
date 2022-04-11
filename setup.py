import setuptools

setuptools.setup(
    name='saaya',
    version='2.0.4',
    author='Jerrita',
    author_email='je5r1ta@icloud.com',
    description='Saaya is a Python framework based on Mirai',
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jerrita/saaya',
    packages=[
        'saaya',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests',
        'colorlog',
        'websockets'
    ],
)
