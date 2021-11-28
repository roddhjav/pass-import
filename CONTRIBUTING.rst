Contributing
============

You want to contribute to pass-import, **thank a lot for this.** You will find
in this page all the useful information needed to contribute to ``pass-import``.


How to run the tests?
---------------------

``pass-import`` has a complete test suite that provide functional and unit tests
for all the parts of the program. Moreover, it provides test coverage and code
health reports.

Tests
~~~~~

To run the tests, you need to install the following programs:

- `python-green`_ as python test runner.
- `python-coverage`_ as code coverage system.

Then simply run: ``make tests``

Code health
~~~~~~~~~~~

To run the code health report, you need to install the following programs:

- `prospector`_ ``pip install prospector[with_everything]``

Then simply run: ``make lint``

Security check
~~~~~~~~~~~~~~

To run the security check, you need to install the following programs:

- `bandit`_ ``pip install bandit``

Then simply run: ``make security``

Generate the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~

To re-generate the README table as well as the man pages and the completion
file simply run: ``make docs``


How to contribute?
------------------

1) If you don't have git on your machine, [install it][git].
2) Fork this repo by clicking on the fork button on the top of this page.
3) Clone the repository and go to the directory:

.. code-block:: console

    git clone  https://github.com/this-is-you/pass-import.git
    cd pass-import

4) Create a branch:

.. code-block:: console

    git checkout -b my_contribution

5) Make the changes and commit:

.. code-block:: console

    git add <files changed>
    git commit -m "A message for sum up my contribution"

6) Push changes to GitHub:

.. code-block:: console

    git push origin my_contribution

7) Submit your changes for review: If you go to your repository on GitHub,
you'll see a Compare & pull request button, fill and submit the pull request.


How to add the support for a new password manager?
--------------------------------------------------

1) To add support for a new password manager named ``mymanager``, add the file
``pass_import/managers/mymanager.py``. The code itself will depend on the
format of the file it should import. Here is the bare minimum for a CSV based
importer:

.. code-block:: python

    # -*- encoding: utf-8 -*-
    # pass import - Passwords importer swiss army knife
    # Copyright (C) Year YourName <you@example.org>.
    #

    from pass_import.formats.csv import CSV
    from pass_import.manager import register_managers


    class MyManagerCSV(CSV):
        """Importer for MyManager in CSV format."""
        name = 'mymanager'
        url='https://mymanager.com'
        hexport='File > Export > CSV'
        himport='pass import mymanager file.csv'
        keys = {
            'title': 'title',
            'password': 'password',
            'login': 'login',
            'url': 'url',
            'comments': 'comments',
            'group': 'group'
        }

        def parse(self):
            # If required your importer code here.
            pass


    register_managers(MyManagerCSV)


2) Then, you will want to import the class ``MyManagerCSV`` in ``pass_import/managers/__init__.py``.

3) Add a file named ``tests/assets/db/mymanager[.csv,.xml,...]``. **No
contribution will be accepted without this file.** This file must contain the
exported data from *your manager*. It has to be the exact export of the main
test password repository. This test data can be found in the
`tests/assets/references/main.yml`.

4) Enable and configure the generic import and file format test for your new
importer. Add an entry in ``tests/tests.yml`` with your importer settings.
**Example**:

.. code-block:: yaml

    MyManagerCSV:
      path: mymanager.csv


5) Check the success of the tests, ensure the coverage does not decrease and the
code health passes.

Naming convention
~~~~~~~~~~~~~~~~~

- The class name is not linked to the command name. It is common to name it as
  follow: ``ManagerNameFormat()``.
- If a class has both import and export capabilities, it is common to name it
  directly by its manager. It should also be the default class for the manager.
- Always sort the classes in alphabetic order.


Data Organization
-----------------

By definition, password-store does not impose any particular schema or type of
organisation of data. Nevertheless, `pass-import` respects the most common case
storing a single password per entry alongside with additional information like
emails, pseudo, URL and other sensitive data or metadata. Although the exact
list of data stored with the password can vary from entries in the password
store, the data imported always respects a simple `key: value` format at the
exception of the password that is always present in the first line.

`pass_import.manager.PasswordManager` is the main class that manages import
from all the supported password manager. Then the classes in
`pass_import.formats` inherit from it. It manages data formatting from all the
password manager.

Data are imported in PasswordManager.data, this is a list of ordered dict. Each
entry is a dictionary that contains the data for a password store entry. The
dictionary's keys are divided into two sets:

1) The *standard keys*: `title`, `password`, `login`, `email`, `url`, `comments`,
`otpauth` and `group`.
2) The *extra* keys that differ from password managers and contain the
description of any extra data we can find in the exported file.


.. _python-green: https://github.com/CleanCut/green
.. _python-coverage: http://nedbatchelder.com/code/coverage/
.. _prospector: https://github.com/PyCQA/prospector
.. _bandit: https://github.com/PyCQA/bandit
.. _git: https://help.github.com/articles/set-up-git/
