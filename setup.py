# -*- encoding: utf-8 -*-

from setuptools import setup

setup(name='youtube_insight',
      version='0.2.0',
      description='An integrated YouTube data crawler',
      author='Siqi Wu',
      author_email='siqi.wu@anu.edu.au',
      url='https://github.com/avalanchesiqi/youtube-insight',
      install_requires=['google-api-python-client>=1.6.4',
                        'urllib3>=1.22',
                        'googletrans>=2.3.0']
      )
