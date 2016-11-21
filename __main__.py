#!/usr/bin/python3

from chaido import *

app = ChaidoApp()
app.load(".chaido")
if len(sys.argv) <= 1:
    print(listToDos(app, []))
else:
    cleanedArguments = sys.argv[2:]
    try:
        print(commands[sys.argv[1]](app, cleanedArguments))
    except ChaidoError as error:
        print("Error: " + error.message)
app.save(".chaido")

