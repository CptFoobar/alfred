# Alfred

Your very own file server.

Alfred is simple file server, useful for serving directory over a network. It is an extension of python's `SimpleHTTPServer` and allows multiple connections simultaneously. It also support multiple command line arguments for increased flexibility.

## Usage

### Using Python script

*(NOTE: You'll be required to install python before you can use alfred. Get it [here](https://www.python.org/downloads/))*

To run using the script, clone this repository (or just download the python script), and place it wherever convenient.

To make Alfred serve the current directory, simple run the following command in your terminal:

```shell
$ python alfred.py serve
```

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

### Using shell script (UNIX systems)

Typing the path to alfred's python script can be tedious. So, as a shorcut, you can set a simple shell script to do it for you. A sample shell script is also present in the repository. Just place the `alfred.py` in the `/opt/alfred/` folder, and then place the `alfred` shell script in your `/usr/bin/` folder.

*You may place `alfred.py` wherever convenient, just make sure to change the path in the `alfred` script*
