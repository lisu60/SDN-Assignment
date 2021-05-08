# Contents

* [What is Git](#what-is-git)
* [How to use Git](#how-to-use-git)
    * [With PyCharm](#with-pycharm)
        * [1. Get a local copy of the repository](#1-get-a-local-copy-of-the-repository)
        * [2. Track files with Git](#2-track-files-with-git)
        * [3. Commit your changes](#3-commit-your-changes)
        * [4. Push your commits](#4-push-your-commits)
        * [5. Update local repository](#5-update-local-repository)
  * [With command line](#with-command-line)
    

# What is Git

Git is a version control tool. It creates "repositories" to store code and all the version changes.
[Github.com](https://github.com) is a website which hosts Git repositories online so that people can collaborate
with Git.

Here describes some basic operations of Git to get started with collaboration using Git.

# How to use Git

## With PyCharm

### 1. Get a local copy of the repository

If it's your first time opening PyCharm, you might see the following window.
Click on "Get from VCS".

![get from vcs](https://github.com/lisu60/SDN-Assignment/blob/master/images/from-vcs-first-open.png?raw=true)

If you don't have that window, you can also archive it by selecting "Git -> Clone...", 
as shown in the following figure:

![clone from git](https://github.com/lisu60/SDN-Assignment/blob/master/images/clone-from-git.png?raw=true)

In the next page, click "GitHub" on the left-hand side to login to GitHub with your GitHub account:

![login github](https://github.com/lisu60/SDN-Assignment/blob/master/images/login-github.png?raw=true)

After loggin in, you should be presented with a list of repositories that are accessible to your account. 
Select the "SDN-Assignment" repository and click "Clone":

![select repo](https://github.com/lisu60/SDN-Assignment/blob/master/images/select-repo.png?raw=true)

Now you should have got a local copy of the repository.

### 2. Track files with Git

When you add a new file to the project, PyCharm automatically asks you if you want to track this file. 
Simply clicking "Add" will do the trick:

![git add file](https://github.com/lisu60/SDN-Assignment/blob/master/images/git-add-file.png?raw=true)

But if you somehow clicked "cancel" and want to add the file later, you can do it through right-clicking on the file:

![add file later](https://github.com/lisu60/SDN-Assignment/blob/master/images/add-file-later.png?raw=true)

### 3. Commit your changes

This is the part where *version control* kicks in.

After you make changes to a file, the file name turns green:

![file name green](https://github.com/lisu60/SDN-Assignment/blob/master/images/file-name-green.png?raw=true)

Now you can make a **commit** of the changes you have made. In Git, whenever you issue a **commit**, you create a new
**version** of the repository. You can revert to any historic version of the repository, in case you make some mistakes in
the future and need to retrieve old files. This is extremely useful in accumulative development and when modifying 
existing code.

To make a commit, select "Git -> Commit". In the pop up dialog, select files you want to include in this commit, and 
write your description of this commit, then click "Commit":

![commit pc](https://github.com/lisu60/SDN-Assignment/blob/master/images/commit-pc.png?raw=true)

You can check all the commits by selecting "Git -> Show Git Log".

### 4. Push your commits

The commit you just made is only stored on your own machine. To publish these changes onto GitHub so that everyone can
sync with you, you need to *push* the commits.

In order to do so, select "Git -> Push". In the pop up dialog, you can review the commits you are about to push:

![push dialog](https://github.com/lisu60/SDN-Assignment/blob/master/images/push-dialog.png?raw=true)

Click "Push" to, well obviously, push.

After this, you can see the changes on the repository page on GitHub:

![push result](https://github.com/lisu60/SDN-Assignment/blob/master/images/push-result.png?raw=true)

### 5. Update local repository

Now someone in the project updated `ryu-app1.py`, you can see it on the GitHub repo page:

![remote modified](https://github.com/lisu60/SDN-Assignment/blob/master/images/remote-modified.png?raw=true)

How do you sync with this change?

You can do it by selecting "Git -> Update Project". After this, you can see newer commits pushed by other users:

![update project](https://github.com/lisu60/SDN-Assignment/blob/master/images/update-project.png?raw=true)
























