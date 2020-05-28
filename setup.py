from setuptools import setup

setup(
    name='bsplayer',
    version='0.0.1',
    packages=['bsplayer'],
    install_requires=['requests', 'logbook', 'click'],
    author='Itai Spiegel',
    author_email='itai.spiegel@gmail.com',
    description='A BSPlayer subtitles API',
    entry_points={
        'console_scripts': [
            'download_subtitles = bsplayer.scripts.download_subtitles:main'
        ]
    }
)
