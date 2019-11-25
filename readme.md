# Digolds web framework

A tiny web framework called **digwebs** which is developed by Python. You can checkout the detail design of **digwebs** in [here](https://www.digolds.cn/detail/0015370868460626a029ac2cf3c42359d4e9fffeae137c7000). You can't use `pip` to install this web framework from PyPI right now, because digwebs is under development and is used to empower the web app called [digolds](https://www.digolds.cn). When more features are added to this framework, we will provide stable package to PyPI where you can use `pip` to install it to your computer.

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

* **digwebs** is where this web framework locate
* **controllers** is where you put controller script
* **middlewares** is where you put middlewares script
* **static** is where you put front end script such as css file, javascript file, font, image etc
* **test** is where you put the test script for your web app
* **views** is where you put the html file

5. run `python .\digwebs.py` to launch the web app demo
6. open your browser and enter `localhost:9999`,you see the content `"digwebs - A Minimal Web Framework!"`

**Note**: if you want to be a master of `digwebs`, head over [here](https://www.digolds.cn/article/00153708688234475cbc5a7d7994e8ebc8b8df6d33a12a1000) to learn the design philosophy of `digwebs`

# Contribution

We are looking for contributors. Please check open issues in the above repos if you think you could help, or open a new one if you have an idea you'd like to discuss.

# License

This project is licensed under the MIT open source license.
