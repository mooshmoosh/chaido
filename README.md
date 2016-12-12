#Chaido - A command line todo list

*Usage*

Add new tasks to your todo list with `chaido new`

```
[user@machine ~]$ chaido new "make a cake"
OK
[user@machine ~]$ chaido new "buy flour"
OK
[user@machine ~]$ chaido new "go to the shops"
OK
[user@machine ~]$ chaido new "buy mixing bowl"
OK
```

Look at the current list of tasks with `chaido`

```
[user@machine ~]$ chaido
1: make a cake
2: buy flour
3: go to the shops
4: buy mixing bowl
```

Cross tasks off with `chaido done`

```
[user@machine ~]$ chaido done 4
OK
[user@machine ~]$ chaido
1: make a cake
2: buy flour
3: go to the shops
```

When you mark off a task as done it will be logged in `.chaido.log`. If you want to delete a task without marking it as done use `chaido remove {task}`.

Hide tasks until another is completed with `chaido must {first task}
before {task to do once the first is done}`

```
[user@machine ~]$ chaido must 2 before 1
OK
[user@machine ~]$ chaido
1: buy flour
2: go to the shops
[user@machine ~]$ chaido must 2 before 1
OK
[user@machine ~]$ chaido
1: go to the shops
```

These hidden tasks will reappear when the tasks they depend on are done

```
[user@machine ~]$ chaido done 1
OK
[user@machine ~]$ chaido
1: buy flour
[user@machine ~]$ chaido done 1
OK
[user@machine ~]$ chaido
1: make a cake
```

Tasks can be bumped up the list to make them more obvious, or to re prioritise.

```
[user@machine ~]$ chaido
1: make a cake
2: buy flour
3: go to the shops
4: buy mixing bowl
[user@machine ~]$ chaido bump 4 before 1
OK
[user@machine ~]$ chaido
1: buy mixing bowl
2: make a cake
3: buy flour
4: go to the shops
```

Tasks can be renamed

```
[user@machine ~]$ chaido
1: make a cake
2: buy flour
3: go to the shops
4: buy mixing bowl
[user@machine ~]$ chaido rename 1 "Bake some cookies"
OK
[user@machine ~]$ chaido
1: Bake some cookies
2: buy flour
3: go to the shops
4: buy mixing bowl
```
