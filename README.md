# Alfred

Your very own file server.

Alfred is simple file server, useful for serving directory over a network. It is an extension of python's `SimpleHTTPServer` and allows multiple connections simultaneously. It also support multiple command line arguments for increased flexibility.

## Usage

*(NOTE: You'll be required to install python before you can use alfred. Get it [here](https://www.python.org/downloads/))*

To run using the script, clone this repository (or just download the [python script](https://github.com/TigerKid001/alfred/blob/master/alfred.py)), and place it wherever convenient.

To make Alfred serve the current directory, simple run the following command in your terminal:

```shell
$ python alfred.py serve
```

If you have set up aliases for alfred (see [how](https://github.com/TigerKid001/alfred#setting-up-aliases)), you can simply run:

```
$ alfred serve
```

To test this, open your broswer and go this url: [http://localhost:8021](http://localhost:8021)

Alfred supports the following parameters:

```
-p, --port : Set the port to run the server on. Defaults to 8021
-d, --directory : Specify directory to be served. Defaults to current working directory
-c, --count-max : Specify maximum number of times directory can be served
-f, --force-port : Force the server to run on the specified port.
                   If this option is used, server won't be started if the port specified is unavailable.
```

So, say you want to serve your downloads directory on port 11155 and only allow it to be served twice, you would run:

```shell
$ python alfred.py serve -p 11155 -c 2 -d ~/Downloads -f
```
Again, having aliases, this can be simplified as:

```shell
$ alfred serve -p 11155 -c 2 -d ~/Downloads -f
```

To test this, open your broswer and go this url: [http://localhost:11155](http://localhost:11155)

## Setting up aliases

Typing the path to alfred's python script everytime you need to serve a directory can be tedious. So, as a shortcut, you can set a terminal alias.

### UNIX Systems

To create an executable for alfred, download the bash script in this [repo](https://github.com/TigerKid001/alfred/blob/master/alfred). Alternatively, create a new bash file `alfred.sh` and add the following lines to it:
```
#!/bin/sh

python /opt/alfred/alfred.py "$@"
```
2. Place the `alfred.py` in the `/opt/alfred/` folder, and then place the `alfred` script in your `/usr/bin/` folder.

*You may place `alfred.py` wherever convenient, just make sure to change the path in the `alfred` script*

To test, you can simply run in your terminal:
```
$ alfred serve
```

### Windows

To set up a command line shortcut for Alfred on Windows, the following steps need to be taken.

1. Download the bat file in the [repo](https://github.com/TigerKid001/alfred/blob/master/alfred.bat). Alternatively, you can create a batch script by creating a file (say `alfred.bat`) and add the following lines to it:
```
@echo off

python "C:\Program Files\alfred\alfred".py %*
```

2. Place the .bat in `C:\Program Files\alfred\`, along with the python file (`alfred.py`).

To make cmd recognize alfred as a command, we need to set a permanent alias for it. For this, do the following:

1. Download the aliases file from this [repo](https://github.com/TigerKid001/alfred/blob/master/cmd_aliases.cmd). Alternatively, create a new file `cmd_aliases.cmd`. In this file, add the following lines:
```
@echo off

DOSKEY alfred="C:\Program Files\alfred\alfred".bat $*
```

The quotes ensure path is interpreted correctly by the command line, and the `$*` simple passes all the arguments following the macro to the actual command.

*You can also add other aliases you may want to set up to this file. See [this](https://en.wikipedia.org/wiki/DOSKEY#Usage) for more on doskey macros*

2. Place this .cmd file in your AppData folder (reach it by typing `%AppData` in the Windows address bar)

3. To make this .cmd file run automatically, open the Run prompt (Windows key + R) and type `regedit` and hit enter.

4. Navigate to HKEY_CURRENT_USER -> Software -> Microsoft -> Command Processor.

5. Create a new entry here by Right Click -> New -> Expandable String Value. Set the name as `AutoRun` and the data as the path to your .cmd file (if you're following the steps as they are, it should be `%AppData%/cmd_aliases.cmd`).

6. That's it. Close the Registry Editor window, close any other terminals you opened, for the changes to take effect.
