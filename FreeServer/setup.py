#coding=utf-8
from setuptools import setup 
setup( 
    name='freeserver',
    py_modules=['__init__', 'freeserver'], 
    install_requires=['pexpect'], 
    entry_points={ 
        'console_scripts': ['freeserver=freeserver:main'] 
        } 
    )
