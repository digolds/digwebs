# Python Web框架【digwebs】

在之前的文章中，我们已经使用了digwebs来快速实现一个简单的网页服务。一开始我们都会借助别人的框架来完成某种服务，通过这种方式，我们可以在一个大的应用场景下认识这些框架，但是要想在编程方面有本质的提升，就必须剖析优秀框架的源码，并且学习其中的设计理念。因此，为了能够更好的使用digwebs框架，接下来的内容将剖析它的每一个组件以及组件之间的关系。

![](http://www.mindfiresolutions.com/blog/wp-content/uploads/8-Python-Web-Frameworks-2018.jpg)

**Digwebs**是一个开源的web框架，它是由Python来开发的，并且托管在[这里](https://github.com/digolds/digwebs)。digwebs的源代码很少，而且容易阅读，此外，在这个系列的文章中也会一点点剖析这个框架的设计思想。读者可以通过学习这个系列的知识来为后续使用Web框架打下良好的基础。运行在digwebs之上的web应用有 [www.digolds.cn](https://www.digolds.cn)。

在这篇文章中，我将带领大家从整体上来认识构成digwebs的组件，以及这些组件之间的关系和作用。接下来让我们从以下这张图开始来认识digwebs中的组件。

![](http://wx4.sinaimg.cn/large/c36a3dc1gy1fyd8rq34obj20qo0f03yp.jpg)

上图揭示了digwebs主要的组件，每一个组件都由一个Python文件定义，每一个Python文件中都会提供类和函数来完成各自的功能。

在上图中，`web.py`封装了所有其它灰色部分模块，同时提供了对外的接口。记住，在开始研究digwebs时，`web.py`是最先开始的地方。在剖析一个框架的时候，你不仅要了解构成这个框架的组件以及它们之间的关系，此外你还得了解这个框架的处理流程。

`digwebs`的处理流程是这样的：`digwebs`启动，此时`web.py`会监听外部事件，当外部事件发生时，`web.py`会解析外部事件发生时的参数，`request.py`会建立一个实例来承载这些参数，紧接着`router.py`会根据这个实例来选择处理路径，每个处理路径是由使用digwebs的人来定义的，最后，`response.py`会根据处理路径返回结果构建一个实例返回给事件发生的地方。

除了以上提及的模块之外，还有一些模块`apis.py`，`errors.py`，`common.py`，`template.py`也提供了辅助的功能，比如`apis.py`定义了一些与restful api相关的方法与类。这些模块起到了辅助作用，是基础模块。

注意，`digwebs`启动的时候，`router.py`和`template.py`会率先初始化，作为一个全局变量，而`request.py`和`response.py`每次处理事件的时候都会重新实例化，作为一个局部变量。

以上通过静态逻辑和动态逻辑从全局上揭示了`digwebs`，为了更好的使用`digwebs`，接下来让我们看看每一个组件的作用以及内部一些具体的定义。

## web.py

这个组件是使用digwebs框架的入口，其中定义了3个关键的元素，它们分别是**类**` digwebs`、**全局变量**`current_app`和`ctx`。
**全局变量**`current_app`是**类**` digwebs`的一个实例，而且每一个web应用都应该只有一个**全局变量**`current_app`。当初始化**全局变量**`current_app`之后，你可以通过**全局变量**`current_app`来使用**类**`digwebs`所定义的方法以及一些装饰器。

为了使用`digwebs`，你需要在一个py文件里写下这些指令，其中digwebs_app就是`current_app`。`digwebs_app.init_all()`的作用是初始化之前提到的模块`router.py`和`template.py`。

```python
from digwebs.web import get_app
dir_path = os.path.dirname(os.path.realpath(__file__))
digwebs_app = get_app({'root_path':dir_path})
digwebs_app.init_all()
digwebs_app.run(9999, host='0.0.0.0')
```

为了配合上面的指令，你需要在另外一个py文件中定义路由事件，并且将这个文件放到目录controllers中。以下例子说明了如何通过**全局变量**`current_app`来使用**类**`digwebs`所定义的装饰器。

```python
from digwebs.web import current_app

@current_app.get('/signout')
def signout():
    ctx.response.delete_cookie(configs.session.name)
    raise seeother('/')
```

其中`@current_app.get('/signout')`就是一个装饰器，这个装饰器的作用是将函数`signout`与`digwebs`建立绑定。触发这个绑定的指令是`digwebs_app.init_all()`，这句指令会在controllers中去查找所有py文件，然后针对每一个文件查找带有类似`@current_app.get('/signout')`指令修饰的函数，然后建立一个**索引表**，而digwebs就是根据这个索引表来完成**路由选择**的。digwebs里除了定义了`get`装饰器，还有其它类型的装饰器，它们有各自的功能，这些装饰器有`view`、`post`、`delete`、`put`、`api`。比如以下例子组合使用了这些装饰器。

下面这段代码定义了一个`blogs.html`页面，同时绑定了函数`list_blogs`。它们一起动态生成了一个html页面，这个页面以列表的形式展示了每一篇文章的概要信息，而这些概要信息由`list_blogs`生成。**注意**，`blogs.html`页面决定了展示内容的形式，而`list_blogs`决定了提供的内容。

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

以上代码片段揭示了装饰器`view`的作用：生成html页面（这个页面中包含了数据部分），并且返回给浏览器。如果有另外一个网站，它想以卡片的形式展示文章，那么它自然希望你的系统能提供文章数据（除去HTML那部分）。此时你需要使用装饰器`api`来帮助你完成这个功能。以下代码片段和上面的代码片段唯一不同的地方在于`@current_app.api`。这个装饰器的作用是：让函数返回**json格式的数据**（不包含HTML部分）。

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

在`web.py`中还有一个全局变量`ctx`，需要了解。`ctx`是一个类型为`threading.local`的变量，它是每次请求的**数据上下文**，每一次请求的数据都会存储在`ctx`上，不同请求的数据之间是独立的，互不影响。只有`ctx`是无法实现不同请求的数据之间的独立性的，还需借助`gunicorn`来实现，`gunicorn`是一个支持wsgi协议的容器，具体内容可以查看[它的官网](https://gunicorn.org/)。

## router.py

这个组件提供了**路由挂接和路由选择**的功能，**路由挂接**是在digwebs启动的时候完成，而**路由选择**是在digwebs启动后并且处理请求时发生的。让我们来举一个例子来理解这2个功能。

假设你正在使用digwebs作为web框架设计一个web app，你为这个web app定义了2个路由处理，它们的事例代码如下所示：

```python
@current_app.get('/')
def home():
    return dict()
		
@current_app.get('/about')
def about():
    return dict()
```
以上代码定义了2个路由，它们分别是`/`和`/about`，每个路由都绑定了对应的处理函数，它们分别是`home`和`about`。digwebs在启动的时候，会自动查找这2个路由，同时将这个两个路由与对应的处理函数绑定起来，这个称为**路由挂接**。当浏览器向服务器发送这2个请求`request('/')`和`request('/about')`，那么**router.py**会根据`/`选择`home`来处理请求`request('/')`，会根据`/about`选择`about`来处理请求`request('/about')`，而这个过程称为**路由选择**。

在`router.py`中你会看到2个关键的**类**`Router`和`Route`。`Router`管理许多`Route`，每一个Route实例就代表了一个路由。`Router`将路由的类型分成2类：动态路由和静态路由，分别由Python的**字典**类型`dynamic_method_to_route`和`static_method_to_route`来表示。此外每种路由的调用方式可以是:`GET`、`POST`、`DELETE`、`PUT`。因此每一个路由都必须说明调用方式，下图就是`Router`为`Route`建立的一个索引关系表。

![](http://wx1.sinaimg.cn/large/c36a3dc1gy1g1vb4yb513j21hb0tzdj5.jpg)

静态路由是形式如下：

```python
@current_app.get('/')
def home():
    return dict()
		
@current_app.get('/about')
def about():
    return dict()
```

而动态路由的形式如下（注意`@current_app.get('/u/:user_id')`中的:user_id）：

```python
@current_app.view('user_profile.html')
@current_app.get('/u/:user_id')
def get_user_profile(user_id):
    u = User.get(user_id)
    for k,v in UserRole.items():
        if v == u.role:
            u['role'] = k
            break
    uies = []
    if u:
        uies = get_user_infos_by(u.id)
    return dict(other_user=u,user_infoes=uies)
```

也就是说，对于以上的动态路由，`/u/123456`和`/u/111111`都会映射到函数`get_user_profile(user_id)`。因此你会发现动态路由最终是放在一个**数组**里。

为了让`web.py`选择路由`Route`，那么需要在`web.py`中初始化`Router`，并且通过`Router`所提供的函数`create_controller`来建立这个**路由表**。一旦这个**路由表**建立了，那么`web.py`就可以通过`Router`来选择`Route`。以下就是完成这一过程的代码片段。

```python
class digwebs(object):
    def __init__(
        self,
        root_path = None,
        template_folder = 'views',
        middlewares_folder= 'middlewares',
        controller_folder = 'controllers',
        is_develop_mode = True):
        '''
        Init a digwebs.

        Args:
          root_path: root path.
        '''

        self.root_path = root_path if root_path else os.path.abspath(os.path.dirname(sys.argv[0]))
        self.middleware = []
        self.template_folder = template_folder
        self.middlewares_folder = middlewares_folder
        self.controller_folder = controller_folder
        self.is_develop_mode = is_develop_mode
        self.template_callbacks = set()
        self.router = None
    
    def init_all(self):
        if self.template_folder:
            self._init_template_engine(os.path.join(self.root_path, self.template_folder))
        
        self.router = Router(self.is_develop_mode)
        self.middleware.append(self.router.create_controller(self.root_path,self.controller_folder,))
        if self.middlewares_folder:
            self._init_middlewares(os.path.join(self.root_path, self.middlewares_folder))
```

重点关注以上代码的这2句指令：

```Python
self.router = Router(self.is_develop_mode)
self.middleware.append(self.router.create_controller(self.root_path,self.controller_folder,))
```

## template.py

在之前的事例代码中我们定义了页面`blogs.html`，这个文件中的内容如下所示：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>digwebs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="keywords" content="python web framework, digwebs web framework,open source web framework,write web service by digwebs"/>
    <meta name="description" content="A tiny web framework called digwebs which is developed by Python."/>
</head>
<body>
    <div id="main" class='uk-container uk-container-small uk-padding'>
    <div class="uk-child-width-1-1 uk-grid-small uk-grid-match" uk-grid>
	    {% for a in template_blogs %}
        <div>
            <div class="uk-card uk-card-default uk-card-body">
                <h3 class="uk-card-title">{{{{a.title}}}}</h3>
                <p>{{{{a.description}}}}</p>
                <a href="{{{{a.detail_link}}}}" class="uk-text-uppercase">Read articles ...</a>
            </div>
        </div>
		{% endfor %}
    </div>
</div>
    {% set static_file_prefix = 'https://cdn.jsdelivr.net/gh/digolds/digresources/' %}
    <link rel="stylesheet" href="{{{{static_file_prefix}}}}/css/uikit.min.css">
    <script src="{{{{static_file_prefix}}}}/js/jquery.min.js"></script>
    <script src="{{{{static_file_prefix}}}}/js/uikit.min.js"></script>
    <script src="{{{{static_file_prefix}}}}/js/uikit-icons.min.js"></script>
</body>

</html>
```

请注意带有花括号的语句，比如`{{{{static_file_prefix}}}}`和`{% for a in template_blogs %}`。这些语句不是`html`指令，因此需要将这些语句转化成`html`指令。`template.py`就是做这件事情的。下图为`template.py`完成这一转化的示意图。

![](http://wx2.sinaimg.cn/large/c36a3dc1gy1g1xdnildmxj20qo0f0wel.jpg)

通过上图可知，`template.py`依赖jinja(它是一个Python库，专门用于合并html和dict数据，最终生成完整的html页面)。接下来我们来分析`template.py`中的关键元素。

`Jinja2TemplateEngine`定义在`template.py`中，在它的构造函数`__init__`中通过以下指令引入了jinja。

```python
from jinja2 import Environment, FileSystemLoader
```

这个类重载了函数`__call__`，这个函数就是用来执行上图的流程的。其中path是`html`页面的路径，比如`/templates/blogs.html`。model是Python中的数据，类型为`dict`，比如之前提到的`return dict(template_blogs=blogs)`。

```python
def __call__(self, path, model):
    return self._env.get_template(path).render(**model).encode('utf-8')
```

当执行以上函数`__call__`之后，返回一个html字符串，这个字符串已经将`{{{{}}}}`之类的指令替换掉，形成一个完整的html字符串。而我们经常看到的类似`{{{{}}}}`之类的指令就是jinja的语法规则。

有了以上概念之后，我们接下来看看`template.py`是如何被调用的。打开`web.py`文件，你会发现以下代码创建了一个`Jinja2TemplateEngine`实例，该实例的名字叫template_engine：

```python
def _init_template_engine(self,template_path):
    self.template_engine = Jinja2TemplateEngine(template_path)
```

创建实例之后，还需要调用`__call__`函数，而以下代码就是调用之处，其中要特别注意这句指令`self.template_engine(r.template_name, r.model)`，这句指令实质上就是调用了函数`__call__`。

```python
def wsgi(env, start_response):
    ctx.application = _application
    ctx.request = Request(env)
    response = ctx.response = Response()
    try:
         r = fn_exec(ctx, None)
         if isinstance(r, Template):
            tmp = []
            for cbf in self.template_callbacks:
                  r.model.update(cbf())
                  r.model['ctx'] = ctx
                  tmp.append(self.template_engine(r.template_name, r.model))
                  r = tmp
	except RedirectError as e:
           response.set_header('Location', e.location)
           start_response(e.status, response.headers)
           return []
```

以上代码还有一处`if isinstance(r, Template)`是需要留意的，为什么r的类型是Template？其原因在于以下代码片段：

```Python
    def view(self, path):
        '''
        A view decorator that render a view by dict.

        >>> @view('test/view.html')
        ... def hello():
        ...     return dict(name='Bob')
        >>> t = hello()
        >>> isinstance(t, Template)
        True
        >>> t.template_name
        'test/view.html'
        >>> @view('test/view.html')
        ... def hello2():
        ...     return ['a list']
        >>> t = hello2()
        Traceback (most recent call last):
        ...
        ValueError: Expect return a dict when using @view() decorator.
        '''

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

其中`@current_app.view('blogs.html')`调用了函数`view`，它是一个装饰器，而函数`view`在digwebs中定义，返回的对象是Template实例，current_app其实是digwebs的一个实例。

## request.py

我们之前经常提到，digwebs会收到来自外部的请求，然后根据请求来选择不同的路由，此外同一个路由接收到的参数会因为用户的不同而不同。为了能够高效的使用提取并使用这些参数，那么需要通过`request.py`来协助我们。接下来我们看看在`request.py`中哪些元素承担了重要角色。

该文件中定义了一个类`Request`，该类提供了解析请求参数和提取参数的相应函数。其中最需要知道的两个函数分别是`_parse_input`和`get`，它们的定义如下：

解析请求参数的代码

```python
    def _parse_input(self):
        def _convert(item):
            if isinstance(item, list):
                return [to_str(i.value) for i in item]
            if item.filename:
                return MultipartFile(item)
            return to_str(item.value)
        fs = CustomFieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        received_data = fs.value
        if isinstance(received_data,list):
            inputs = dict()
            for key in fs:
                inputs[key] = _convert(fs[key])
        else:
            raise ValueError('unknown received data type')
        return inputs
```

提取请求参数的代码

```python
    def get(self, key, default=None):
        '''
        The same as request[key], but return default value if key is not found.

        >>> from StringIO import StringIO
        >>> r = Request({'REQUEST_METHOD':'POST', 'wsgi.input':StringIO('a=1&b=M%20M&c=ABC&c=XYZ&e=')})
        >>> r.get('a')
        u'1'
        >>> r.get('empty')
        >>> r.get('empty', 'DEFAULT')
        'DEFAULT'
        '''
        r = self._get_raw_input().get(key, default)
        if isinstance(r, list):
            return r[0]
        return r
```

一般情况下，解析请求参数的函数`_parse_input`会自动被提取参数函数`get`调用，因此我们只需要直接使用`get`函数就能够提取我们想要的参数。接下来，让我们看看`request.py`是如何被集成到`web.py`中的。打开`web.py`文件，你会发现以下代码片段:

```python
def wsgi(env, start_response):
    ctx.application = _application
    ctx.request = Request(env)
```

该片段实例化了Request，变量存储在ctx上，叫request。此外该片段还说明了一件事，每次请求都会重新实例化Request，而且之前的request与下一次的request都是不同的，通过这一点我们就可以将每次请求都独立开来。当ctx中存有变量request后，那么后续的路由处理过程中就可以通过ctx来取得request，并且通过request提取到当前请求的参数。

## response.py

当digwebs接收到外部请求，并且处理该请求，最终得到一个结果，这个结果会返回给谁呢？一般情况下，浏览器可以发送请求，而且浏览器期望返回的结果是html页面，有时也期望是一个文件。除此之外，第三方应用发送请求，并期望通过digwebs返回json格式的数据。由此可以看出，digwebs可以返回多种格式的结果，为了区分这些格式，模块`response.py`定义了一个类`Response`，这个类记录了返回数据的格式，数据长度以及状态码。有了这些记录返回数据的元数据，那么digwebs就可以统一地将这些元数据返回给发起请求方，比如浏览器，第三方应用。

与类`Request`一样，类`Response`也是在每一次请求处理的过程中实例化的。我们需要关注这个类中所定义的2个成员变量，它们分别是`self._status`和`self._headers = {'CONTENT-TYPE': 'text/html; charset=utf-8'}`。

`_status`这个变量记录了返回的状态码，这些状态码定义在`response_code.py`里。这些状态码的定义如下：

```python
# all known response statues:
RESPONSE_STATUSES = {
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',

    # Redirection
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: "I'm a teapot",
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended',
}
```

`_headers`这个变量是用来记录数据格式、数据长度、数据编码等信息的。

前面我们提到过，类`Response`是在每一次请求的过程中实例化的，而这个实例化发生的过程体现在`web.py`中`response = ctx.response = Response()`：

```python
def wsgi(env, start_response):
    response = ctx.response = Response()
	  start_response(response.status, response.headers)
	  return r
```

由此可以看到，使用者只需要调用`ctx.response`来记录`_status`和`_header`信息，然后再调用`start_response`函数将这些信息返回给发起请求的源头，此时这些源头就知道所传输的数据是什么格式以及该数据的长度。只有知道这些信息，这些源头才能选择相应的策略来解析数据。上面代码还有一部分`return r`需要留意，其中的`r`就是数据部分，这部分数据和response中的数据共同返回给发起请求方，使得它能够拿到数据以及数据的格式，选择相应的解析策略来解析数据。

## apis.py，errors.py，common.py

之前介绍了digwebs的关键构成组件，那些组件是需要深入了解的，而这一节中的组件只需要大概了解。

`apis.py`是一个定义了与restful相关的类，这些类主要代表了某类错误，比如`APIPermissionError`就代表了权限相关的错误。在这个文件中定义的类一般只会用在`@current_app.api`所修饰的路由中。

`errors.py`中也定义了很多类，与`apis.py`类似，这些类代表了某种类型的错误，它们一般只会用在`@current_app.view`所修饰的路由中。

`common.py`中定义了常用的工具函数，这些函数经常被digwebs的很多地方使用，因此会将这些常用的函数提取到这个模块中。这种方法是模块复用的一个简单的事例。

## 总结

当你阅读到这里之后，相信你已经迷惑了，那么不妨通过以下图片再来简单回顾一下digwebs的2个过程**启动过程**和**处理请求的过程**：

![](http://wx4.sinaimg.cn/large/c36a3dc1gy1fyd8rq34obj20qo0f03yp.jpg)

**digwebs启动过程**

1.获取全局对象digwebs_app

```python
from digwebs.web import get_app
dir_path = os.path.dirname(os.path.realpath(__file__))
digwebs_app = get_app({'root_path':dir_path})
```

2.初始化digwebs_app所有依赖的组件,这些组件有`router.py`和`template.py`。其中`router.py`的主要任务是建立路由表，而`template.py`的主要任务是启动渲染html页面的实例。

```python
digwebs_app.init_all()
```

3.启动digwebs_app

```python
digwebs_app.run(9999, host='0.0.0.0')
```

**digwebs处理请求的过程**

1.digwebs接收到外部的请求，接收的请求入口在`web.py`中

```python
def wsgi(env, start_response)
```

2.接收到请求之后，实例化`request.py`和`response.py`中的类，其中`Request`负责解析接收到的数据，`Response`负责返回处理结果

```python
ctx.request = Request(env)
response = ctx.response = Response()
```

3.根据`ctx.request`的内容，由`route.py`中的`Router`来选择路由

```python
                def dispatch(i):
                    fn = self.middleware[i][0]
                    if i == len(self.middleware):
                        fn = next
                    return fn(context, lambda: dispatch(i + 1))
```

4.将处理的结果返回给请求发起方

```python
start_response(response.status, response.headers)
return r
```
