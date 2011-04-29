from setuptools import setup

setup(
    name='rapidsms-ureport',
    version='0.1',
    license="BSD",

    install_requires = [
        "rapidsms",
        'django-eav',
        'rapidsms-polls',
    ],

    dependency_links = [
        "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
        "http://github.com/daveycrockett/rapidsms-polls/tarball/master#egg=rapidsms-polls",
    ],

    description='The uReport social advocacy program deployed in Uganda.',
    long_description=open('README.rst').read(),
    author='David McCann',
    author_email='david.a.mccann@gmail.com',

    url='http://github.com/daveycrockett/rapidsms-ureport',
    download_url='http://github.com/daveycrockett/rapidsms-ureport/downloads',

    include_package_data=True,

    packages=['ureport'],
    package_data={'ureport':['templates/*/*.html','templates/*/*/*.html']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
