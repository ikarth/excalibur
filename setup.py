
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Excalibur: A NaNoGenMo 2016 Novel Generator',
    'author': 'Isaac Karth',
    'url': 'https://github.com/ikarth/excalibur',
    'download_url': 'https://github.com/ikarth/excalibur',
    'author_email': 'isaac@isaackarth.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['excalibur'],
    'scripts': [],
    'name': 'excalibur'
}

setup(**config)
