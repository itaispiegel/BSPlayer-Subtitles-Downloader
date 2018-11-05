from setuptools import setup

setup(
    name='bsplayer',
    version='0.0.1',
    packages=['bsplayer'],
    requires=['requests', 'logbook', 'struct', 'click'],
    author='Itai Spiegel',
    author_email='itai.spiegel@gmail.com',
    description='A BSPlayer subtitles API'
)
