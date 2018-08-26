# Bluelog

*A blue blog.*

Demo: http://bluelog.helloflask.com

![Screenshot](http://helloflask.com/screenshots/bluelog.png)

## Installation

```
$ git clone https://github.com/greyli/bluelog.git
$ cd bluelog
$ pipenv install --dev
$ pipenv shell
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/
```

Test account:

* username: `admin`
* password: `helloflask`


## For Chinese Readers of My Flask Book

这个仓库包含[《Flask Web开发实战》](http://helloflask.com/book)第8章的示例程序Bluelog的源码。

仓库中的Git标签（tag）按照书中的章节推进设置，你可以在书中相应位置看到对应标签的签出提示。请阅读前言中的《如何使用示例程序》一节了解具体操作。

如果执行`pipenv install`命令安装依赖耗时太长，你可以考虑使用国内的PyPI镜像源，比如：
```
$ pipenv install --dev --pypi-mirror https://mirrors.aliyun.com/pypi/simple
```

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
