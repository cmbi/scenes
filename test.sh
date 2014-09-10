#!/bin/bash
export SCENES_SETTINGS="scenes_settings.json"
nosetests --with-coverage --cover-package=yas_scenes
