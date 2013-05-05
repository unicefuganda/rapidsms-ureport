#from setuptools import setup, find_packages
from setuptools import find_packages
from distutils.core import setup

setup(
    name='rapidsms-ureport',
    version='0.1',
    license="BSD",

    install_requires=[
        "rapidsms",
        'django-eav',
        'rapidsms-polls',
        'rapidsms-httprouter',
        'rapidsms-unregister',
        'rapidsms-auth',
        'rapidsms-script',
        'django-extensions',
        'django-uni-form',
        'rapidsms-unregister',
        'rapidsms-contact',
        'rapidsms-generic',
        'uganda-common',
        'xlrd',
    ],

    dependency_links=[
        "http://github.com/mvpdev/django-eav/tarball/master#egg=django-eav",
        "http://github.com/unicefuganda/rapidsms-polls/tarball/master#egg=rapidsms-polls",
        "http://github.com/unicefuganda/rapidsms-httprouter/tarball/master#egg=rapidsms-httprouter",
        "http://github.com/unicefuganda/rapidsms-unregister/tarball/master#egg=rapidsms-unregister",
        "http://github.com/unicefuganda/rapidsms-polls/tarball/master#egg=rapidsms-polls",
        "http://github.com/unicefuganda/rapidsms-contact/tarball/master#egg=rapidsms-contact",
        "http://github.com/unicefuganda/rapidsms-generic/tarball/master#egg=rapidsms-generic",
        "http://github.com/unicefuganda/rapidsms-script/tarball/master#egg=rapidsms-script",
        "http://github.com/unicefuganda/uganda_common/tarball/master#egg=uganda-common",
        "http://github.com/unicefuganda/auth/tarball/master#egg=rapidsms-auth",
    ],

    scripts=["ureport-admin.py", "ureport-install.sh"],

    description='The uReport social advocacy program deployed in South Sudan.',
    long_description=open('README.rst').read(),
    author='Engulu Paul',
    author_email='askpaul82@gmail.com',

    url='http://github.com/unicefuganda/rapidsms-ureport',
    download_url='http://github.com/unicefuganda/rapidsms-ureport/downloads',

    include_package_data=True,

    packages=find_packages(),
    package_data={'ureport':['templates/*/*.html', 'templates/*/*/*.html', 'static/*/*']},
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
