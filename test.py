#!/usr/bin/python3

import unittest
import chaido

class MockChaiDoApp(chaido.ChaidoApp):
    def load(self, filename):
        return

    def save(self, filename):
        return

class CleanArgumentsTest(unittest.TestCase):
    def testCleanArgumentsToAddTodo(self):
        arguments = ["buy", "more", "milk", "-d", "5"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk", "-d", "5"])

    def testCleanArgumentsWithATodoAndMultipleOptions(self):
        arguments = ["buy", "more", "milk", "-d", "5", "3", "9"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk", "-d", "5", "3", "9"])

    def testCleanArgumentsOnlyArguments(self):
        arguments = ["-buy", "-more", "-milk", "-d", "-5"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, arguments)

    def testCleanArgumentsNoOptions(self):
        arguments = ["buy", "more", "milk", "ok?"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk ok?"])

    def testCleanEmptyArguments(self):
        arguments = []
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, [])

class ChaidoAdding(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()

    def testAddATodo(self):
        chaido.addNewTodo(self.app, ["buy more milk"])
        self.assertEqual(self.app.totalTodoCount, 1)
        self.assertEqual(self.app.getTodo(0), "buy more milk")

    def testAddATodoWithADependant(self):
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "-b", "buy more milk"])
        self.assertEqual(self.app.totalTodoCount, 2)
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        self.assertEqual(self.app.visibleTodoCount, 1)

    def testAddATodoWithASpecifiedWithIndex(self):
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "-b", "2"])
        self.assertEqual(self.app.totalTodoCount, 3)
        self.assertEqual(self.app.getTodo(0), "write a book")
        self.assertEqual(self.app.getTodo(1), "go to the shops")
        self.assertEqual(self.app.visibleTodoCount, 2)

class ChaidoRemoving(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "-b", "buy more milk"])

    def testRemovingATodo(self):
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        chaido.removeTodo(self.app, ["1"])
        self.assertEqual(self.app.totalTodoCount, 1)
        self.assertEqual(self.app.getTodo(0), "buy more milk")

class ChaidoListTodos(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["write a book"])

    def testListingTwoTasks(self):
        expectedResult = """1: buy more milk
2: write a book"""
        self.assertEqual(chaido.listToDos(self.app, []), expectedResult)
        chaido.addNewTodo(self.app, ["go to the shops", "-b", "buy more milk"])

if __name__ == "__main__":
    unittest.main()
