Sumo Logic Contentmap
=====================

Every wanted to get a map of the number of Dashboards, queries, and other content in your Sumo Logic organization?
Contentmap can help you; it is a wrapper around the Sumo Logic API to get you that information at your fingertips.

The script will give you a name, type, a path, and the ID for the content and the parent folder.
Armed with this, you can manage your content as you want, when you want.

And, coupled with other scripts, you can publish this map into Sumo Logic as a category, so you can track your content development.

Installing the Scripts
=======================

These scripts designed to be used within a batch script or DevOPs tool such as Chef or Ansible.
Each script is a python3 script, and the complete list of the python modules are provided to aid people using a pip install.

You will need to use Python 3.6 or higher and the modules listed in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6 or higher from python.org. Append python3 to the LIB and PATH env.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install the scripts.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies:
    
        sudo -H pip3 install pipenv 
 
    5. Clone this repository. This will create a new folder
    
    6. Change into this folder. Type the following to install all the package dependencies 
       (this may take a while as this will download all of the libraries it uses):

        pipenv install
        
Dependencies
============

See the contents of "pipfile"

Script Names and Purposes
=========================

The scripts are organized into sub directories:

    1. ./bin - has all of the scripts
          ./bin/sumocontentmap.py
    2. ./etc - has an example of a config file to set ENV variables for access
    3. ./var - will contain helper materials


Examples and How to Use the Scripts
===================================

    1. display help message
          ./bin/sumocontentmap.py -h

    2. specify the org name, and credentials
          ./bin/sumocontentmap.py -a <API_UID>:<API_SECRET> -e <ENDPOINT> -k <SUMO_ORGID>

    3. add extra verbosity to the output
          ./bin/sumocontentmap.py -a <API_UID>:<API_SECRET> -e <ENDPOINT> -k <SUMO_ORGID> -v <VERBOSE_LEVEL>

To Do List:
===========

* extend to all global folders

* extend output into CSV, JSON files in addition to STDOUT

* incorporate support for credential managers, such as SSM

* provide a lambda version of this

License
=======

Copyright 2022 Wayne Kirk Schmidt

Licensed under the Apache 2.0 License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    license-name   Apache 2.0 
    license-url    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

Feel free to e-mail me with issues to: wschmidt@sumologic.com
I will provide "best effort" fixes and extend the scripts.

