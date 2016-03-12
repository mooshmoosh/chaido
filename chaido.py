#!/usr/bin/python3

import sys
import os
import json

class ChaidoError(BaseException):
    def __init__(self, message):
        self.message = message

def addNewTodo(app, arguments):
    if len(arguments) < 1:
        return "No todo item was provided"
    newTodoIndex = app.addTodo(arguments[0])
    if len(arguments) >= 3 and arguments[1] == '-b':
        try:
            app.addDependantTasks(newTodoIndex, arguments[2:])
        except ChaidoError:
            return "Error: " + ChaidoError.message
    return "OK"

def removeTodo(app, arguments):
    while len(arguments) > 0:
        app.removeTodo(arguments.pop(0))
    return "OK"

def displayHelp(app, arguments):
    pass

def listToDos(app, arguments):
    result = []
    counter = 1
    for todo in app.todoItems:
        result.append(str(counter) + ": " + todo['name'])
        counter += 1
    return "\n".join(result)

commands = {
    "new" : addNewTodo,
    "done" : removeTodo,
    "help" : displayHelp,
    "list" : listToDos,
}

def cleanUpArguments(argumentList):
    argumentsToJoin = []
    result = []
    for (index, arg) in enumerate(argumentList):
        if arg.startswith("-"):
            if len(argumentsToJoin) > 0:
                result.append(" ".join(argumentsToJoin))
                argumentsToJoin = []
            result += argumentList[index:]
            break
        else:
            argumentsToJoin.append(arg)
    if len(argumentsToJoin) > 0:
        result.append(" ".join(argumentsToJoin))

    return result

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class ChaidoApp:
    def __init__(self):
        self.todoItems = []
        self.totalTodoCount = 0

    def addTodo(self, todoName):
        newTodoIndex = len(self.todoItems)
        self.todoItems.append({"name" : todoName, "children" : []})
        self.totalTodoCount += 1
        return newTodoIndex

    def removeTodo(self, todoName):
        taskIndex = self.getTaskIndexByIdentifier(todoName)
        taskToRemove = self.todoItems.pop(taskIndex)
        self.todoItems += taskToRemove["children"]
        self.totalTodoCount -= len(taskToRemove["children"])

    def getTaskIndexByIdentifier(self, todoIdentifier):
        if isInt(todoIdentifier):
            return int(todoIdentifier) - 1
        else:
            return self.getTaskIndexByName(todoIdentifier)

    def getTaskIndexByName(self, task):
        for index, todo in enumerate(self.todoItems):
            if todo.get("name") == task:
                return index
        raise ChaidoError("No visible task named " + task)

    @property
    def visibleTodoCount(self):
        return len(self.todoItems)

    def getTodo(self, index):
        if index > self.visibleTodoCount:
            raise ChaidoError("There are fewer than " + str(index) + " visible todos")
        return self.todoItems[index].get("name")

    def addDependantTasks(self, dependantTask, depended):
        dependantTaskObject = self.todoItems.pop(dependantTask)
        dependedTaskObjects = []
        taskIndexesToPop = []
        for task in depended:
            taskIndex = self.getTaskIndexByIdentifier(task)
            dependedTaskObjects.append(self.todoItems[taskIndex])
            taskIndexesToPop.append(taskIndex)
        dependantTaskObject["children"] = dependedTaskObjects
        taskIndexesToPop.sort(reverse=True)
        for idx in taskIndexesToPop:
            self.todoItems.pop(idx)
        self.todoItems.append(dependantTaskObject)

    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.loads(f.read())
            if 'items' not in data or 'itemcount' not in data:
                return
            self.todoItems = data['items']
            self.totalTodoCount = data['itemcount']

    def save(self, filename):
        data = {}
        data['items'] = self.todoItems
        data['itemcount'] = self.totalTodoCount
        with open(filename, "w") as f:
            f.write(json.dumps(data))

if __name__ == "__main__":
    app = ChaidoApp()
    app.load(".chaido")
    if len(sys.argv) <= 1:
        print(listToDos(app, []))
    else:
        cleanedArguments = cleanUpArguments(sys.argv[2:])
        print(commands[sys.argv[1]](app, cleanedArguments))
    app.save(".chaido")

