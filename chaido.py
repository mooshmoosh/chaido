import re
import sys
import os
import json
import version
import data_migration
from Exceptions import *

def addNewTodo(app, arguments):
    if len(arguments) < 1:
        raise ChaidoError("No todo item was provided")
    newTodoIndex = app.addTodo(arguments[0])
    if len(arguments) >= 3 and arguments[1] == 'before':
        app.setTaskAsDependant(newTodoIndex, arguments[2:])
        highest_priority = app.getTaskPriority(arguments[2])
        for task in arguments[2:]:
            task_priority = app.getTaskPriority(task)
            if task_priority < highest_priority:
                highest_priority = task_priority
        app.setTaskPriority(newTodoIndex, highest_priority)
    return "OK"

def addNewTodoToTop(app, arguments):
    if len(arguments) < 1:
        raise ChaidoError("No todo item was provided")
    newTodoIndex = app.addTodo(arguments[0])
    if len(arguments) >= 3 and arguments[1] == 'before':
        app.setTaskAsDependant(newTodoIndex, arguments[2:])
    app.setTaskPriority(newTodoIndex, app.getTaskPriority("1") - 1)
    return "OK"

def removeTodoWithoutLogging(app, arguments):
    while len(arguments) > 0:
        app.removeTodo(arguments.pop(0), log=False)
    return "OK"

def removeTodo(app, arguments):
    while len(arguments) > 0:
        app.removeTodo(arguments.pop(0))
    return "OK"

def displayHelp(app, arguments):
    pass

def listToDos(app, arguments):
    if app.visibleDirty:
        app.recalculateVisible()
    result = []
    for counter, todo in enumerate(app.getVisibleTodos()):
        if len(arguments) > 0 and arguments[0] == 'short':
            todo_name = str(app.todoItems[todo]['name'])
            todo_words = todo_name.split(' ')
            todo_number = str(counter + 1)
            result.append(todo_number + ": " + ' '.join(todo_words[0:7]))
            for word_bunch in range(7,len(todo_words), 7):
                result.append(' ' * (len(todo_number) + 2) + ' '.join(todo_words[word_bunch:word_bunch + 7]))
        else:
            result.append(str(counter + 1) + ': ' + str(app.todoItems[todo]['name']))
    return "\n".join(result)

def listAllToDos(app, arguments):
    result = []
    for task_index in sorted(list(app.todoItems.keys())):
        result.append(str(app.todoItems[task_index]['name']))
    return "\n".join(result)

def setTaskAsDependant(app, arguments):
    if "then" in arguments:
        taskLists = [[]]
        for argument in arguments:
            if argument == 'then':
                taskLists.append([])
            else:
                taskLists[-1].append(argument)
        if len(taskLists) < 2:
            raise ChaidoError("Syntax is {tasks to do first} then {tasks to do later} ... then ... etc")
        for taskListNumber, taskList in enumerate(taskLists[:-1]):
            for beforeTask in taskList:
                app.setTaskAsDependant(beforeTask, taskLists[taskListNumber + 1])
    else:
        listingBeforeTasks = True
        beforeTasks = []
        afterTasks = []
        if "before" not in arguments:
            raise ChaidoError("Syntax is {tasks to do first} before {tasks to do later}")
        for argument in arguments:
            if argument == 'before':
                listingBeforeTasks = False
            elif listingBeforeTasks:
                beforeTasks.append(argument)
            else:
                afterTasks.append(argument)
        if len(afterTasks) == 0:
            raise ChaidoError("You must specify task(s) that depend on " + dependant)
        for beforeTask in beforeTasks:
            app.setTaskAsDependant(beforeTask, afterTasks)
    return "OK"

def bumpTodo(app, arguments):
    if 'before' in arguments:
        listingBeforeTasks = True
        beforeTasks = []
        afterTasks = []
        for argument in arguments:
            if argument == 'before':
                listingBeforeTasks = False
            elif listingBeforeTasks:
                beforeTasks.append(argument)
            else:
                afterTasks.append(argument)
        max_priority = app.getTaskPriority(afterTasks[0])
        for afterTask in afterTasks:
            if max_priority > app.getTaskPriority(afterTask):
                max_priority = app.getTaskPriority(afterTask)
        for beforeTask in beforeTasks:
            app.setTaskPriority(beforeTask, max_priority - 1)
    else:
        for argument in arguments:
            app.bumpTodo(argument)
    return "OK"

def renameTodo(app, arguments):
    if len(arguments) < 2:
        raise ChaidoError("You must specify a task, and the new name for the task")
    taskIndex = app.getTaskIndexByIdentifier(arguments[0])
    app.setTaskName(taskIndex, arguments[1])
    return "OK"

def pushTodoDown(app, arguments):
    if len(arguments) == 0:
        raise ChaidoError("You must specify a task to push down the list")
    if 'after' in arguments:
        beforeTasks = []
        afterTasks = []
        for argument in arguments:
            if argument == 'after':
                listingBeforeTasks = False
            elif listingBeforeTasks:
                beforeTasks.append(argument)
            else:
                afterTasks.append(argument)
        if len(afterTasks) == 0:
            raise ChaidoError("You must specify task(s) that you want to push these after")
        for beforeTask in beforeTasks:
            app.pushTaskAfter(beforeTask, afterTasks)
    else:
        for argument in arguments:
            app.pushTaskToBottom(argument)
    return "OK"

commands = {
    "new" : addNewTodoToTop,
    "later" : addNewTodo,
    "done" : removeTodo,
    "help" : displayHelp,
    "list" : listToDos,
    "all" : listAllToDos,
    "bump" : bumpTodo,
    "must" : setTaskAsDependant,
    "rename" : renameTodo,
    "remove" : removeTodoWithoutLogging,
    "push" : pushTodoDown,
}

def cleanUpArguments(argumentList):
    argumentsToJoin = []
    result = []
    for (index, arg) in enumerate(argumentList):
        if arg in ['before', 'then'] or isInt(arg):
            if len(argumentsToJoin) > 0:
                result.append(" ".join(argumentsToJoin))
                argumentsToJoin = []
            if isInt(arg):
                result.append(int(arg))
            else:
                result.append(arg)
        elif re.match(r'^\d+-\d+$', arg):
            start_range = int(arg.split('-')[0])
            end_range = int(arg.split('-')[1]) + 1
            result += list(range(start_range, end_range))
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
        self.todoItems = {}
        self.visibleTodoItems = []
        self.visibleDirty = False
        self.nextTodoIndex = 0
        self.next_max_priority = -1
        self.logMessages = []

    def getLogMessages(self):
        return self.logMessages

    def log(self, command, message):
        self.logMessages.append({
            "command" : command,
            "message" : message
        })

    @property
    def totalTodoCount(self):
        if self.visibleDirty:
            self.recalculateVisible()
        return len(self.todoItems)

    @property
    def visibleTodoCount(self):
        if self.visibleDirty:
            self.recalculateVisible()
        return len(self.visibleTodoItems)

    def setTaskName(self, taskIndex, newName):
        oldName = self.todoItems[taskIndex]['name']
        self.todoItems[taskIndex]['name'] = newName
        self.log("rename", "\t".join([oldName, newName]))

    def getVisibleTodos(self):
        if self.visibleDirty:
            self.recalculateVisible()
        return self.visibleTodoItems

    def addTodo(self, todoName):
        self.todoItems[str(self.nextTodoIndex)] = {"name" : todoName, "children" : [], "priority" : self.nextTodoIndex}
        self.visibleTodoItems.append(str(self.nextTodoIndex))
        self.nextTodoIndex += 1
        self.log("new", todoName)
        return len(self.visibleTodoItems)

    def bumpTodo(self, todoName):
        self.visibleDirty = True
        taskIndex = self.getTaskIndexByIdentifier(todoName)
        self.todoItems[taskIndex]['priority'] -= 1

    def getTaskPriority(self, todoName):
        taskIndex = self.getTaskIndexByIdentifier(todoName)
        return self.todoItems[taskIndex]['priority']

    def setTaskPriority(self, todoName, newPriority):
        self.visibleDirty = True
        taskIndex = self.getTaskIndexByIdentifier(todoName)
        self.todoItems[taskIndex]['priority'] = newPriority

    def pushTaskAfter(self, beforeTask, afterTasks):
        lowest_priority = None
        for task in afterTasks:
            task_priority = self.getTaskPriority(task)
            if lowest_priority is None:
                lowest_priority = task_priority
            elif lowest_priority < task_priority
                lowest_priority = task_priority
        self.setTaskPriority(beforeTask, lowest_priority)

    def removeTodo(self, todoName, log=True):
        self.visibleDirty = True
        taskIndex = self.getTaskIndexByIdentifier(todoName)
        if taskIndex not in self.todoItems:
            raise ChaidoError("No such task: " + todoName)
        if log:
            self.log("done", self.todoItems[taskIndex]['name'])
        del self.todoItems[taskIndex]

    def setTaskAsDependant(self, beforeTask, afterTasks):
        self.visibleDirty = True
        beforeTaskIndex = self.getTaskIndexByIdentifier(beforeTask)
        for afterTask in afterTasks:
            afterTaskIndex = self.getTaskIndexByIdentifier(afterTask)
            if afterTaskIndex == beforeTaskIndex:
                continue
            self.log('set_dependant', self.todoItems[afterTaskIndex]['name'] + "\t" + self.todoItems[beforeTaskIndex]['name'])
            self.todoItems[afterTaskIndex]['children'].append(beforeTaskIndex)

    def getTaskIndexByIdentifier(self, todoIdentifier):
        if isInt(todoIdentifier):
            return self.visibleTodoItems[int(todoIdentifier) - 1]
        else:
            return self.getTaskIndexByName(todoIdentifier)

    def getTaskIndexByName(self, task):
        for index, todo in self.todoItems.items():
            if todo.get("name") == task:
                return index
        raise ChaidoError("No visible task named " + task)

    def pushTaskToBottom(self, taskName):
        self.visibleDirty = True
        taskIndex = self.getTaskIndexByIdentifier(taskName)
        self.setTaskPriority(taskName, self.todoItems[self.visibleTodoItems[-1]]['priority'] + 1)

    def recalculateVisible(self):
        self.visibleTodoItems = sorted(self.todoItems.keys(), key=(lambda x : int(self.todoItems[x]['priority'])))
        for index, todoItem in self.todoItems.items():
            newChildrenList = []
            for child in todoItem['children']:
                if child in self.todoItems:
                    newChildrenList.append(child)
            todoItem['children'] = newChildrenList
            if len(newChildrenList) > 0:
                self.visibleTodoItems.remove(index)
        self.visibleDirty = False

    def getTodo(self, index):
        if self.visibleDirty:
            self.recalculateVisible()
        if index > len(self.visibleTodoItems):
            raise ChaidoError("There are fewer than " + str(index) + " visible todos")
        return self.todoItems[self.visibleTodoItems[index]].get("name")

    def addDependantTasks(self, dependantTask, depended):
        newIndex = self.addTodo(dependantTask)
        self.todoItems[newIndex]['children'].append(
            [self.getTaskIndexByIdentifier(task) for task in depended]
        )

    def load(self, filename):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.loads(f.read())
            if '__format_version__' not in data:
                data['__format_version__'] = 0
            if data['__format_version__'] <= version.__format_version__:
                data = data_migration.migrate_old_data(data)
            self.todoItems = data.get('todo_items', {})
            self.visibleTodoItems = data.get('visible_todo_items', [])
            self.nextTodoIndex = data.get('next_todo_index', 0)
            self.visibleDirty = data['visible_dirty']
            self.next_max_priority = data['next_max_priority']

    def save(self, filename):
        data = {}
        data['visible_dirty'] = self.visibleDirty
        data['todo_items'] = self.todoItems
        data['visible_todo_items'] = self.visibleTodoItems
        data['next_todo_index'] = self.nextTodoIndex
        data['next_max_priority'] = self.next_max_priority
        data['__format_version__'] = version.__format_version__
        with open(filename, "w") as f:
            f.write(json.dumps(data))

