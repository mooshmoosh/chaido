#Chaido - A todo list manager for hackers

*Usage*

Add new tasks to your todo list with `chaido new`

```
$ chaido new make a cake
OK
$ chaido new buy flour
OK
$ chaido new go to the shops
OK
$ chaido new buy mixing bowl
OK
```

Look at the current list of tasks with `chaido`

```
$ chaido
1: make a cake
2: buy flour
3: go to the shops
4: buy mixing bowl
```

Cross tasks off with `chaido done`

```
$ chaido done 4
OK
$ chaido
1: make a cake
2: buy flour
3: go to the shops
```

Hide tasks until another is completed with `chaido must {later task} -b {task to do before}`

```
$ chaido must 3 -b 2
OK
$ chaido
1: make a cake
2: go to the shops
$ chaido must 2 -b 1
OK
$ chaido
1: go to the shops
```

These hidden tasks will reappear when the tasks they depend on are done

```
$ chaido don 1
OK
$ chaido
1: buy flour
$ chaido done 1
OK
$ chaido
1: make a cake
```

