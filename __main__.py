#!/usr/bin/python3

import datetime
from chaido import *

app = ChaidoApp()
app.load(".chaido")
if len(sys.argv) <= 2:
    print(listToDos(app, []))
    app.save(".chaido")
else:
    cleanedArguments = cleanUpArguments(sys.argv[2:])
    if sys.argv[1] not in commands:
        print("Unknown command " + sys.argv[1])
        exit()
    try:
        print(commands[sys.argv[1]](app, cleanedArguments))
        with open(".chaido.log", 'a') as f:
            for logMessage in app.getLogMessages():
                f.write("|".join([datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"), logMessage['command'], logMessage['message']]) + "\n")
        app.save(".chaido")
    except ChaidoError as error:
        print("Error: " + error.message)
