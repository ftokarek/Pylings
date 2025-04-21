## v1.1.1
  - badge for deploying to pylings
  - updated workflow for better deployment

## v1.1.0

- refactoring
  - pylint score improved from 7.54 to 9.86
  - removed deadcode from pylings.utils.handle_args
  - pylings.init.update_workspace
    - now produces better messaging
  - README 
    - corrected spelling errors
    - added image of `pylings update`

- new command
  - reset
    - you can call reset `pylings reset <exercise-path>`, this is the same as the internal `r`

- new workflow
  - python-build
    - When release is created i GH, release now propogates to pip

## v1.0.5

- updated exercise
  - 01_variables3.py
    - fixed error in strings comparsion 

## v1.0.4

- Each exercise directory has a README that contains useful information about that exercsie for the user to refer to
- new exercises:
  - 03_functions/functions{3,4,5}.py
  - 04_conditionals/conditionals4.py
- updated exercises:
  - 04_conditionals/conditionals{1,2,3}.py

## v1.0.3

- hints are formatted better with rich formatted text
- fleshed out a couple of hints.

## v1.0.2

- fixed path resolution for run, dry-run and sol commands

## v1.0.1

- pylings is now a pip package!
- new commands:
  - `update`
    - updates the workspace with the current version in `/path/to/<site-packages,bin>`
  - `--debug`
    - enables debug logging for advanced output, log file is workspace `.pylings_debug.log`
- python is invoked by sys.executable for better cross platform support
- update to layout and instructions
- README, now has badges!

## v1.0.0

Initial Release