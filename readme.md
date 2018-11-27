# Digolds web framework

A tiny web framework called **digwebs** which is developed by Python. You can't use `pip` to install this web framework from PyPI right now, because digwebs is under development and is used to empower the web app called [digolds](https://www.digolds.cn). When more features are added to this framework, we will provide stable package to PyPI where you can use `pip` to install it to your computer.

As a developer, you can also use `git` to `pull` this repository to your computer, then follow below steps to quickly boost this framework.

1. Install Python 3.6.x to your computer
2. Use `git` to pull the source
3. Run `pip install jinja2` to install jinja2 to your computer
4. Run `python .\digwebs\project_generator.py` to generate the project file structure
This step will generate project layout like below:
```
.
  |-controllers
  |-digwebs
  |-middlewares
  |-static
  |  |-css
  |  |-fonts
  |  |-images
  |  |-js
  |-test
  |-views
```
* digwebs is where this web framework locate
* controllers is where you put controller script
* middlewares is where you put middlewares script
* static is where you put front end script such as css file, javascript file, font, image etc
* test is where you put the test script for your web app
* views is where you put the html file

5. run `python .\digwebs.py` to lanch the web app demo
6. open your browser and enter `localhost:9999` to checkout the result