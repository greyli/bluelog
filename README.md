# Bluelog

*A blue blog.*

> Example application for *[Python Web Development with Flask](http://helloflask.com/en/book)* (《[Flask Web 开发实战](http://helloflask.com/book)》).

Demo: http://bluelog.helloflask.com

![Screenshot](http://helloflask.com/screenshots/bluelog.png)

## Installation

clone:
```
$ git clone https://github.com/greyli/bluelog.git
$ cd bluelog
```
create & activate virtual env then install dependency:

with venv/virtualenv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```
or with Pipenv:
```
$ pipenv install --dev
$ pipenv shell
```
generate fake data then run:
```
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/
```

Test account:

* username: `admin`
* password: `helloflask`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
