# Contributing to Pylings

First off, thanks for taking the time to contribute! ❤️

## Quick Reference

I want to …

- _report a bug!_ ➡️ [open an issue](#issues)
- _fix a bug!_ ➡️ [open a pull request](#pull-requests)
- _implement a new feature!_ ➡️ [open an issue to discuss it first, then a pull request](#issues)
- _add an exercise!_ ➡️ [read this](#adding-an-exercise)
- _update an outdated exercise!_ ➡️ [open a pull request](#pull-requests)

## Issues

You can open an issue [here](https://github.com/compeng0001/pylings/issues/new).
If you're reporting a bug, please include the output of the following commands:

- `py --version`
- `ls -la`
- Your OS name and version

## Pull Requests

You are welcome to open a pull request, but unless it is small and trivial, **please open an issue to discuss your idea first** 🙏🏼

Opening a pull request is as easy as forking the repository and committing your changes.
If you need any help with it or face any Git related problems, don't hesitate to ask for help 🤗

It may take time to review your pull request.
Please be patient 😇

When updating an exercise, check if its solution needs to be updated.

## Adding An Exercise

- Name the file `exercises/yourTopic/yourTopicN.rs`.
- Make sure to put in some helpful links, and link to sections of The Book in `exercises/yourTopic/README.md`.
- In the exercise, add a `// TODO: …` comment where user changes are required.
- Copy `exercises/yourTopic/yourTopicN.rs` to `backups/yourTopic/yourTopicN.rs`
- Add a solution at `solutions/yourTopic/yourTopicN.rs` with comments explaining it.
- Add the [metadata for your exercise](#exercise-metadata) in the `pylings/config/config.toml` file.
- Make sure your exercise runs
- [Open a pull request](#pull-requests).

### Exercise Metadata

The exercise metadata should contain the following, and be in sorted list:

```toml
[exercises]
name = "yourTopicN"
dir = "yourTopic"
hint = """
Multiline is supported

This is more readable than using \n on one continous line
""""
```
