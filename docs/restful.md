# digwebs中的Restful机制实现

一个web框架需要支持Restful特性，比如常见的Get，Post，Put，Delete操作。这些操作具体的含义分别是取、追加，更新，删除资源，而且这些操作都是基于http(s)协议的。这些操作是针对资源的，为了让这些资源以某种格式呈现出来需要定义2个装饰器view和api。digwebs定义了6个装饰器get，post，put，delete，view，api，使用这6个装饰器，你可以使用digwebs来指定提供何种**类型**的操作，操作之后的**数据格式**为什么。

![](http://wx4.sinaimg.cn/large/c36a3dc1gy1g3xakdnhv8j20nl0eiwgj.jpg)

接下来本篇文章将分以下部分来讲解digwebs的Restful特性以及如何修饰数据格式：

1. digwebs的6大装饰器
2. Restful之get装饰器
3. Restful之post装饰器
4. Restful之put装饰器
5. Restful之delete装饰器
6. 数据格式装饰器-view
7. 数据格式装饰器-api

## digwebs的6大装饰器

```python
class digwebs(object):
    def get(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'GET'
            return func

        return _decorator

    def post(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'POST'
            return func

        return _decorator

    def put(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'PUT'
            return func

        return _decorator

    def delete(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'DELETE'
            return func

        return _decorator

    def view(self, path):
        def _decorator(func):
            @functools.wraps(func)
            def _wrapper(*args, **kw):
                r = func(*args, **kw)
                if isinstance(r, dict):
                    logging.info('return Template')
                    return Template(path, **r)
                raise ValueError(
                    'Expect return a dict when using @view() decorator.')

            return _wrapper

        return _decorator
    
    def api(self,func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            try:
                r = json.dumps(func(*args, **kw))
            except APIError as e:
                r = json.dumps(dict(error=e.error, data=e.data, message=e.message))
            except Exception as e:
                logging.exception(e)
                r = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=str(e)))
            ctx.response.content_type = 'application/json'
            return r
        return _wrapper
```

由上面的代码片段可以看到digwebs这个类中定义了6个装饰器，显而易见，这6个装饰器的作用就是对应上文的Restful特性以及格式定义的特性。它们分别是：

Restful特性分别对应：get、post、put、delete
格式定义的特性对应：view和api

当digwebs提供了以上6大特性之后，使用者可以在自己的服务里自定义资源操作和呈现的格式。比如在之前的文章中获取博客文章列表的操作以及格式的具体定义如下：

```python
@current_app.view('blogs.html')
@current_app.get('/views/blogs')
def list_blogs():
	blogs = []
	blogs.append({
	'title':'What is digwebs',
	'description':'A tiny web framework called digwebs which is developed by Python.',
	'detail_link':'######'})
	blogs.append({
	'title':'Why you should use digwebs',
	'description':'Digwebs is a Python web framework, which you can use to accelerate the development process of building a web service.',
	'detail_link':'######'})
	blogs.append({'title':'How to use digolds web framework','description':'You can use digwebs in a few steps. First pull the source code. Second install jinja2. Finally run python .\digwebs\project_generator.py to generate the project file structure.','detail_link':'######'})
	return dict(template_blogs=blogs)
```

@current_app.get('/views/blogs')的作用是将路径`/views/blogs`与函数`list_blogs`绑定。
@current_app.view('blogs.html')的作用是将函数`list_blogs`返回的数据格式化为HTML。

以上2句代码就是使用了Restful的get特性以及格式化特性。其含义是我的服务中有一项服务，这项服务是**获取（get）**博客文章数据，用户通过路径**/views/blogs**便可以获取这些数据，这些数据将以**html的形式（view）**返回给用户，提供服务的人只需要定义如何获取这些数据的**方法（list_blogs）**。

接下来让我们看看get、post、put、delete的区别，以及view和api的区别。

## Restful之get装饰器

digwebs中的get装饰器对应HTTP中的GET方法。根据规范GET方法有以下要求：

1. 只允许获取资源，不允许修改资源
2. 资源的格式可以是XML，JSON
3. 成功获取资源需要返回状态码200 (OK)，如果无法获取资源需要根据具体情况返回404 (资源不存在) or 400 (错误的请求)

因此当你使用digwebs中的get装饰器时，它就默认满足以上条件，也就是说你不允许在自定义的处理函数中编写涉及到改变资源的代码，这样就违反了以上规范。

digwebs中的get装饰器也是定义在类digwebs中，具体的代码片段如下：

```python
class digwebs(object):
    def get(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'GET'
            return func

        return _decorator
```

使用digwebs中的get装饰器的例子如下：

```python
@current_app.get('/')
def hello_world():
    return 'hello digwebs!'
```

## Restful之post装饰器

digwebs中post装饰器对应HTTP中的POST方法。根据规范POST方法有以下要求：

1. POST方法用于创建新的资源
2. POST方法一般用于创建子资源（比如为一篇文章创建评论）
3. POST方法执行成功之后，将返回状态码201
4. 相同的POST方法，相同的参数，返回的结果不一定一样

因此根据以上规则，当你使用digwebs的POST装饰器时，就应该很清楚地知道资源是可以被修改的，而且每次相同的POST请求，对资源的改变是不一样的。

以下是digwebs中post装饰器的定义：

```python
class digwebs(object):
    def post(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'POST'
            return func

        return _decorator
```

使用digwebs中post装饰器的例子如下：

```python
@current_app.post('/:article_id/comment')
def create_new_comment(article_id):
    # create a comment for the specific article
```

## Restful之put装饰器

digwebs中put装饰器对应HTTP中的PUT方法。根据规范PUT方法有以下要求：

1. PUT方法用于更新资源，若没有资源则创建一个新的资源（比如更新一篇文章内容）
2. PUT方法执行成功之后，当更新资源时应返回状态码200，如果新建资源时应返回状态码201
3. 相同的PUT方法，相同的参数，其执行结果是一样的。

因此根据以上规则，当你使用digwebs的PUT装饰器时，就应该很清楚地知道资源是可以被修改的，而且每次相同的PUT请求，对资源的改变是一样的。

以下是digwebs中put装饰器的定义：

```python
class digwebs(object):
    def put(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'PUT'
            return func

        return _decorator
```

使用digwebs中put装饰器的例子如下：

```python
@current_app.put('/article')
def update_an_article():
    # update the specific article
```

## Restful之delete装饰器

digwebs中delete装饰器对应HTTP中的DELETE方法。根据规范DELETE方法有以下要求：

1. DELETE方法用于删除资源
2. DELETE方法执行成功之后，应返回状态码200，若没有发现资源则返回状态码404
3. 相同的DELETE方法，相同的参数，其执行结果是一样的。

以下是digwebs中delete装饰器的定义：

```python
class digwebs(object):
    def delete(self, path):
        def _decorator(func):
            func.__web_route__ = path
            func.__web_method__ = 'DELETE'
            return func

        return _decorator
```

使用digwebs中delete装饰器的例子如下：

```python
@current_app.delete('/article')
def delete_an_article():
    # delete the specific article
```

## 数据格式装饰器-view

获取的资源的格式决定了其浏览的工具，我们大部分时间都会通过浏览器来浏览信息，这些信息其实就是资源，只不过这些资源是通过不同的服务器获取的，那么为了让digwebs返回的资源能够被浏览器消化，那么应该提供一款装饰器view，它的目的在于将资源以html的格式返回。下面就是digwebs中view装饰器的定义：

```python
class digwebs(object):
    def view(self, path):
        def _decorator(func):
            @functools.wraps(func)
            def _wrapper(*args, **kw):
                r = func(*args, **kw)
                if isinstance(r, dict):
                    logging.info('return Template')
                    return Template(path, **r)
                raise ValueError(
                    'Expect return a dict when using @view() decorator.')

            return _wrapper

        return _decorator
```

使用该装饰器的例子如下：

```python
@current_app.view('blogs.html')
@current_app.get('/views/blogs')
def list_blogs():
	blogs = []
	blogs.append({
	'title':'What is digwebs',
	'description':'A tiny web framework called digwebs which is developed by Python.',
	'detail_link':'######'})
	blogs.append({
	'title':'Why you should use digwebs',
	'description':'Digwebs is a Python web framework, which you can use to accelerate the development process of building a web service.',
	'detail_link':'######'})
	blogs.append({'title':'How to use digolds web framework','description':'You can use digwebs in a few steps. First pull the source code. Second install jinja2. Finally run python .\digwebs\project_generator.py to generate the project file structure.','detail_link':'######'})
	return dict(template_blogs=blogs)
```

## 数据格式装饰器-api

除了资源能给浏览器使用之外，还有其它应用需要使用这些资源，但是这些应用不希望这些资源夹杂着html的标签信息，而期望原始资源。为了让不同应用能够消化相同的资源，此时需要一种格式，这种格式不仅能够被不同应用解析，而且能够保留原始资源。目前比较流行的格式有json，而digwebs中的装饰器api则使用了这一格式，api的定义如下：

```python
class digwebs(object):
    def api(self,func):
        @functools.wraps(func)
        def _wrapper(*args, **kw):
            try:
                r = json.dumps(func(*args, **kw))
            except APIError as e:
                r = json.dumps(dict(error=e.error, data=e.data, message=e.message))
            except Exception as e:
                logging.exception(e)
                r = json.dumps(dict(error='internalerror', data=e.__class__.__name__, message=str(e)))
            ctx.response.content_type = 'application/json'
            return r
        return _wrapper
```

使用digwebs装饰器api的例子如下：

```python
@current_app.api
@current_app.get('/views/blogs')
def list_blogs():
	blogs = []
	blogs.append({
	'title':'What is digwebs',
	'description':'A tiny web framework called digwebs which is developed by Python.',
	'detail_link':'######'})
	blogs.append({
	'title':'Why you should use digwebs',
	'description':'Digwebs is a Python web framework, which you can use to accelerate the development process of building a web service.',
	'detail_link':'######'})
	blogs.append({'title':'How to use digolds web framework','description':'You can use digwebs in a few steps. First pull the source code. Second install jinja2. Finally run python .\digwebs\project_generator.py to generate the project file structure.','detail_link':'######'})
	return dict(template_blogs=blogs)
```
