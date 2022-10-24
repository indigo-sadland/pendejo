# pendejo - Pentaho RCE POC

This project is based on [ginger](https://github.com/HawSec/ginger) but with essential modification of BeanShell code for getting better RCE expirience (which was lacking during one of my penetration testing).

## Usage

Pendejo has only one mandatory parameter, the URL of the target Pentaho installation:

```console
python3 pendejo.py http://localhost:8080/pentaho
```

**Note: do not include a trailing slash (/)**

```console
python3 pendejo.py http://localhost:8080/pentaho -u admin -p password
```

When Pendejo establishes a connection with Pentaho BA, it will prompt and wait for commands.
I've left only one command - `cmd`.

Command | Reference
--- | ---
cmd | execute cmd command. (Example: ```dir 'C:\\\\Windows'```)
