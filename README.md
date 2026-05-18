# Config

A config file will be generated in your `$XDG_CONFIG_HOME` path (`$HOME/.config`):

```shell
$HOME/.config/config.ini
---
[paths]
movies = 
shows = 
```

# Python Notes
## venv
Start the environment:
```shell
. .venv/bin/activate
```

# Testing

Use the included `duplicate_tree.sh` script to duplicate a directory tree with files of a specified size.

# Build

Use `pyinstaller` to build into a `moniker` distributable.

```shell
pyinstaller main.spec
```

Build is in `dist` (ie `dist/moniker`)

`main.spec` configures the pyinstaller.

Note: There are specific configuration values in `main.spec` for including binaries (.so files) and the `style.css` data file.