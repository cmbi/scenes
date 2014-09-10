# Scenes

**scenes** creates [YASARA][1] scenes using WHAT IF [list databank][2] files.
It uses the python api distributed with YASARA.

# License

To be decided.

# Pre-requisites

* [YASARA][1]. The currently supported scenes can be created
  with YASARA View. Make sure you have at least version 14.7.17.

# Installation

## From source

Download the source code and run the python installer:

* `wget https://github.com/cmbi/scenes/releases/scenes-<version>.tar.gz`
* `tar -zxvf scenes-<version>.tar.gz`
* `cd scenes-<version>`
* `python setup.py install`

* Specify the path to your local YASARA installation in a json
  settings file (an example `scenes_settings.json` is provided).
* Set the envvar `SCENES_SETTINGS` to the path to the json settings file.
* Run: `scenes`

# Development

If you'd like to contribute by adding features or fixing bugs, follow the steps
in this section to setup a development environment.

## Pre-requisites

The following pre-requisites are required by bdb and must be installed
manually:

* virtualenv
* virtualenvwrapper
* YASARA (see above)

## Setup

* Run `mkvirtualenv --no-site-packages scenes` to create a virtual
  environment, and switch to that environment with `workon scenes`.
* Run `git clone https://github.com/cmbi/scenes.git` to obtain the latest
  source code.
* Run `git checkout develop` to switch to the development branch. It's also
  recommended that you create a feature branch off develop.
* Run `pip install -r requirements` to install the module dependencies.
  This command installs the required module dependencies into the virtual
  environment you've created, isolating the development environment from the
  rest of your system.
* Setup the environment so that the local YASARA installation can be found
  (see above).

## Run

A script `run.sh` is provided for development runs. The script sets
`SCENES_SETTINGS` to the development settings `scenes_settings.json`.

## Tests

A script `test.sh` is provided for development tests. The sripts sets
`SCENES_SETTINGS` to the development settings `scenes_settings.json`.


[1]: http://www.yasara.org
[2]: http://swift.cmbi.ru.nl/gv/lists/
