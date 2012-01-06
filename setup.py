try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(
  name="emoji-python",
  version="0.2.0",
  author="najeira",
  author_email="najeira@gmail.com",
  description=u"A library to convert japanese emoji.",
  license="Apache License 2.0",
  keywords=["japanese", "emoji", "pictogram"],
  url="http://code.google.com/p/emoji-python/",
  platforms='any',
  zip_safe=False,
  include_package_data=True,
  packages=['emoji', 'emoji.convert', 'emoji.data'],
  package_data={'': ['img/docomo/*', 'img/ezweb/*']},
  )
