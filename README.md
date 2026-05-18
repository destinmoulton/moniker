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
source .venv/bin/activate
```

# Testing

Use the included `duplicate_tree.sh` script to duplicate a directory tree with files of a specified size.

# Installing

Use `pip` to install from requirements.txt.

```shell
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```