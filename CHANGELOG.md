## v1.2.1
- Fix for list view not updating when not current exercise, was indexed exercise. Will also update entire list when called.
- Progress bar updates with respect to DONE and PENDING correctly
- Some extra logging

## v1.2.0
- add dynamic theme support with `themes.toml` configuration
- replace hardcoded colour constants with dynamic theme loading
- add support for storing active theme in `.pylings.toml`
- add multiple built-in colour themes
- enable user to specify their own theme in `pylings.toml`
- update UI to apply theme background colors
- clean up screen styles and add horizontal padding for better layout
- fix f-string quote and backslash escape for Python <3.12 compatibility
- add `None` check for `importlib.util.find_spec` origin to avoid type errors

## v1.1.2
  - fix variable name mismatch in {backups,exercises,solutions}\variables5.py
  - fix update message
  - add code of conduct

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