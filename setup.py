from setuptools import setup, find_packages

setup(name='df_raw_decoder',
      version='0.1',
      description='DF raw decoder package forked from github.com/kateby/df_raw_decoder',
      url='https://github.com/dfint/df_raw_decoder',
      author='kateBy, insolor',
      author_email='insolor@gmail.com',
      license='MIT',
      packages=find_packages(),
      test_requirements=['pytest', 'pytest-cov'],
      zip_safe=False)
