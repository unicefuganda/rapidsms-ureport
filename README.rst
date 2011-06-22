Ureport
=======
Ureport is a user-centered social monitoring tool designed to strengthen community-led development and citizen engagement. It allows users to speak out on what is happening in their community and feeds back useful information to assist users to enact change in your community.

Technically speaking, Ureport leverage the work of rapidsms-polls (github.com/daveycrockett/rapidsms-polls/) to provide an easy system for polling a large number of users, and adds a visualization layer to aggregate poll results exposed in as JSON in the polling app.

A running example of ureport can be viewed at ureport.ug

Requirements
============
 - Python 2.6 (www.python.org/download/) : On linux machines, you can usually use your system's package manager to perform the installation
 - MySQL or PostgreSQL are recommended
 - All other python libraries will be installed as part of the setup and configuration process
 - Some sort of SMS Connectivity, via an HTTP gateway.  By default, Ureport comes configured to work with a two-way clickatell number (see http://www.clickatell.com/downloads/http/Clickatell_HTTP.pdf and http://www.clickatell.com/downloads/Clickatell_two-way_technical_guide.pdf).  Ideally, you want to obtain a local short code in your country of operation, or configure Ureport to use a GSM modem (see http://docs.rapidsms.org for more information on how to do this).
Installation
============
Before installation, be sure that your clickatell two-way callback points to::

     http://yourserver.com/ureport/clickatell/

This is essential if you want to receive incoming messages.

It's highly recommended that you use a virtual environment for a Ureport project.  To set this up, create the folder where you want your Ureport project to live, and in a terminal, within this folder, type::

    ~/Projects/ureport$ pip install virtualenv
    ~/Projects/ureport$ virtualenv env
    ~/Projects/ureport$ source env/bin/activate

Ureport can be installed from a terminal or command prompt using::

    ~/Projects/ureport$ pip install -e git+http://github.com/daveycrockett/rapidsms-ureport#egg=ureport

Configuration
=============


For linux, the provided ureport-install.sh script can be run immediately after installation::

    ~/Projects/ureport$ ureport-install.sh

This will do some basic configuration to get your install up-and-running.  It makes some assumptions about the configuration of whatever database software you've installed, so if you're more confident with performing each step manually, here's a summary of what the script does:

 - Patches Django 1.3 (a bug that prevents the Ureport visualizations for working, acceptance pending)
 - Creates a project folder for Ureport (running ureport-admin.py startproject ureport-project)
 - Tweaks the settings.py file in your project to your parameters (settings.DATABASES, clickatell account information)
 - Creates the database tables (running manage.py syncdb)
 - Runs the server (running manage.py runserver)

After you've completed this configuration, you should be able to point your browser to http://localhost:8000/ and see your Ureport install up and running!  To start uploading users, click on the "ureporters" tab to upload a spreadsheet.

