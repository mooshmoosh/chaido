#!/usr/bin/python3

import data_migration
import json
import os
import unittest
import chaido
import version

class MockChaiDoApp(chaido.ChaidoApp):
    def load(self, filename):
        return

    def save(self, filename):
        return

class CleanArgumentsTest(unittest.TestCase):
    def testCleanArgumentsToAddTodo(self):
        arguments = ["buy", "more", "milk", "before", "5"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk", "before", 5])

    def testCleanArgumentsWithATodoAndMultipleOptions(self):
        arguments = ["buy", "more", "milk", "before", "5", "3", "9"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk", "before", 5, 3, 9])

    def testCleanArgumentsNoOptions(self):
        arguments = ["buy", "more", "milk", "ok?"]
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, ["buy more milk ok?"])

    def testCleanEmptyArguments(self):
        arguments = []
        cleanedArguments = chaido.cleanUpArguments(arguments)
        self.assertEqual(cleanedArguments, [])

    def testMultiWordTodo(self):
        args = ["Go", "to", "the", "shops", "before", "buy", "some", "milk"]
        self.assertEqual(chaido.cleanUpArguments(args), ["Go to the shops", "before", "buy some milk"])

    def testNumberedTodos(self):
        args = ["1", "2", "3", "4", "5", "Go", "to", "the", "shops", "6", "before", "7", "8", "9"]
        self.assertEqual(chaido.cleanUpArguments(args), [1, 2, 3, 4, 5, "Go to the shops", 6, "before", 7, 8, 9])

    def testNumberedRangeTodos(self):
        args = ["1", "2-4", "9", "before", "hello"]
        self.assertEqual(chaido.cleanUpArguments(args), [1, 2, 3, 4, 9, "before", "hello"])

class ChaidoAdding(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()

    def testAddATodo(self):
        chaido.addNewTodo(self.app, ["buy more milk"])
        self.assertEqual(self.app.totalTodoCount, 1)
        self.assertEqual(self.app.getTodo(0), "buy more milk")

    def testAddATodoWithADependant(self):
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "before", "buy more milk"])
        self.assertEqual(self.app.totalTodoCount, 2)
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        self.assertEqual(self.app.visibleTodoCount, 1)

    def testAddATodoWithASpecifiedWithIndex(self):
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "before", "2"])
        self.assertEqual(self.app.totalTodoCount, 3)
        self.assertEqual(self.app.getTodo(0), "write a book")
        self.assertEqual(self.app.getTodo(1), "go to the shops")
        self.assertEqual(self.app.visibleTodoCount, 2)

    def testAddMultipleTodoWithASpecifiedWithIndex(self):
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "before", "1", "2"])
        self.assertEqual(self.app.totalTodoCount, 3)
        self.assertEqual(self.app.visibleTodoCount, 1)
        self.assertEqual(self.app.getTodo(0), "go to the shops")

    def testAddNewTodoAtTheTopOfTheList(self):
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodoToTop(self.app, ["go to the shops"])
        self.assertEqual(self.app.totalTodoCount, 3)
        self.assertEqual(self.app.visibleTodoCount, 3)
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        self.assertEqual(self.app.getTodo(1), "write a book")
        self.assertEqual(self.app.getTodo(2), "buy more milk")

class ChaidoRemoving(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["go to the shops", "before", "buy more milk"])

    def testRemovingATodo(self):
        self.assertEqual(self.app.visibleTodoCount, 1)
        self.assertEqual(self.app.totalTodoCount, 2)
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        chaido.removeTodo(self.app, ["1"])
        self.assertEqual(self.app.totalTodoCount, 1)
        self.assertEqual(self.app.visibleTodoCount, 1)
        self.assertEqual(self.app.getTodo(0), "buy more milk")

    def testRemovingTasksThatDontExist(self):
        chaido.removeTodo(self.app, ["1"])
        chaido.removeTodo(self.app, ["2"])
        with self.assertRaises(chaido.ChaidoError):
            chaido.removeTodo(self.app, ["1"])
        self.assertEqual(self.app.totalTodoCount, 0)

    def testRemovingMultipleTasksInNonDecreasingOrder(self):
        chaido.addNewTodo(self.app, ["buy more cheese"])
        chaido.addNewTodo(self.app, ["buy more eggs"])
        chaido.addNewTodo(self.app, ["buy more flour"])
        self.assertEqual(self.app.visibleTodoCount, 4)
        self.assertEqual(self.app.totalTodoCount, 5)
        self.assertEqual(self.app.getTodo(0), "go to the shops")
        self.assertEqual(self.app.getTodo(1), "buy more cheese")
        self.assertEqual(self.app.getTodo(2), "buy more eggs")
        self.assertEqual(self.app.getTodo(3), "buy more flour")

        chaido.removeTodo(self.app, ["1", "2", "3"])
        self.assertEqual(self.app.visibleTodoCount, 2)
        self.assertEqual(self.app.totalTodoCount, 2)
        self.assertEqual(self.app.getTodo(0), "buy more milk")
        self.assertEqual(self.app.getTodo(1), "buy more flour")


class ChaidoListTodos(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["write a book"])

    def testListingTwoTasks(self):
        expectedResult = """1: buy more milk
2: write a book"""
        self.assertEqual(chaido.listToDos(self.app, []), expectedResult)
        chaido.addNewTodo(self.app, ["go to the shops", "before", "buy more milk"])

class ChaidoSetExistingTaskAsDependant(unittest.TestCase):
    def setUp(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy pens"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["go to the shops"])

    def testSetTaskAsDependant(self):
        chaido.setTaskAsDependant(self.app, ["3", "before", "2"])
        self.assertEqual(self.app.visibleTodoCount, 3)
        self.assertEqual(self.app.totalTodoCount, 4)
        self.assertEqual(self.app.getTodo(0), "buy pens")
        self.assertEqual(self.app.getTodo(1), "write a book")
        self.assertEqual(self.app.getTodo(2), "go to the shops")

    def testSetTaskAsDependantOnMultipleTasks(self):
        chaido.setTaskAsDependant(self.app, ["3", "before", "1", "2"])
        self.assertEqual(self.app.visibleTodoCount, 2)
        self.assertEqual(self.app.totalTodoCount, 4)
        self.assertEqual(self.app.getTodo(0), "write a book")
        self.assertEqual(self.app.getTodo(1), "go to the shops")

    def testSetMulipleTasksAsDependantOnMultipleTasks(self):
        chaido.setTaskAsDependant(self.app, ["3", "4", "before", "1", "2"])
        self.assertEqual(self.app.visibleTodoCount, 2)
        self.assertEqual(self.app.totalTodoCount, 4)
        self.assertEqual(self.app.getTodo(0), "write a book")
        self.assertEqual(self.app.getTodo(1), "go to the shops")

class ChaidoTestMigrations(unittest.TestCase):
    def testMigrationFrom1To2(self):
        old_format = {
          "__format_version__": 1,
          "visible_todo_items": [
            "0",
            "1",
            "2",
            "3"
          ],
          "next_todo_index": 4,
          "visible_dirty": False,
          "todo_items": {
            "0": {
              "children": [],
              "name": "buy pens"
            },
            "3": {
              "children": [],
              "name": "go to the shops"
            },
            "2": {
              "children": [],
              "name": "write a book"
            },
            "1": {
              "children": [],
              "name": "buy more milk"
            }
          }
        }
        version.__format_version__ = 2
        new_format = data_migration.migrate_old_data(old_format)
        self.assertEqual(new_format['__format_version__'], 2)
        for index, todo in new_format['todo_items'].items():
            self.assertEqual(todo['priority'], int(index))
        self.assertEqual(new_format['next_max_priority'], -1)

class ChaidoListingAllTaskTests(unittest.TestCase):
    def testListingAllTasks(self):
        self.app = MockChaiDoApp()
        chaido.addNewTodo(self.app, ["buy pens"])
        chaido.addNewTodo(self.app, ["buy more milk"])
        chaido.addNewTodo(self.app, ["write a book"])
        chaido.addNewTodo(self.app, ["go to the shops"])
        chaido.setTaskAsDependant(self.app, ["4", "before", "1"])
        self.assertEqual(chaido.listToDos(self.app, []), """1: buy more milk
2: write a book
3: go to the shops""")
        self.assertEqual(chaido.listAllToDos(self.app, []), """buy pens
buy more milk
write a book
go to the shops""")


if __name__ == "__main__":
    unittest.main()
