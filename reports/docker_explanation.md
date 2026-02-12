# Why Dockerization is Necessary

You are asking why Docker is needed. It’s because the current code allows ANY user to run ANY command on your computer.

## The Problem: `exec()`

In `execution_service.py`, your code does this:

```python
exec(user_source, global_ns)
```

This takes whatever text the user typed and runs it directly on your server.

## A Real Example of What Goes Wrong

Imagine I am a student. I type this into the practice room:

```python
import os
import shutil
# This deletes your entire project folder
shutil.rmtree("C:/Users/Mochitha vijayan/Client_Server_Practice_Rooms - 3")
```

If you run this without Docker **your project is gone**. Permanently.

## How Docker Fixes It

Docker puts the code in a "box".

1.  **Isolation**: The code runs in a separate, empty Linux environment.
2.  **Protection**: If the user runs `rm -rf /`, they only delete the *empty box*, not your computer.
3.  **Safety**: The code cannot access your files, your network, or your database.

That is why Docker is mandatory for allowing users to run code.
