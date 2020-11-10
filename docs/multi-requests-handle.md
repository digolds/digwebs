# digwebs多个请求的处理机制
                            
当启动一个服务的时候，应该满足同时处理多个用户发送的请求，比如针对一个网站，有的用户访问了该网站的主页，有的用户访问了该网站的其它页面，而且这些用户是同时访问的。不同用户访问，会发起不同的请求，服务拿到这些不同的请求就会产生不同的响应，因此需要有一个机制能够将成对的请求+响应区别开来，也就是说用户A的请求+响应应该与用户B的请求+响应是相互独立的。

![](http://wx4.sinaimg.cn/large/c36a3dc1gy1g46buo6403j20ti0e9wff.jpg)

为了区别对待请求+响应，逻辑实现上应该是这样：定义一个类Request来代表用户的请求，定义一个类Response来代表响应，每一次的请求响应需要存储在一个变量上，服务可以从这个变量（这个变量应该具有区分不同请求响应的功能）上取到请求，并且根据该请求生成对应的响应。其中这种类型的变量就是我们这篇文章要引进的：`threading.local()`。

接下来这篇文章将从定义`threading.local()`变量开始，接着分析digwebs是如何使用这种变量来处理不同的请求的。
      
## 线程上下文数据 - threading.local()

`threading.local()`创建的变量具有一个特性，也就是不同的线程独立持有该变量。想要使用`threading.local()`变量，你只需要创建一个该类型的变量，然后将数据存储在这个变量的属性上。比如以下代码：

```python
import threading
mydata = threading.local()
mydata.x = 1
mydata.request = Request()
mydata.response = Response()
```

其中x,request,response就是你想设置的数据，数据类型可以是任意的。当你定义了一个`threading.local()`类型的变量，不同的线程就会复制该变量，并占为己有。以下事例说明了这一特性：

```python
import threading
import logging
import random

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-0s) %(message)s',)

def show(d):
    try:
        val = d.val
    except AttributeError:
        logging.debug('No value yet')
    else:
        logging.debug('value=%s', val)

def f(d):
    show(d)
    d.val = random.randint(1, 100)
    show(d)

if __name__ == '__main__':
    d = threading.local()
    show(d)
    d.val = 999
    show(d)
    for i in range(2):
        t = threading.Thread(target=f, args=(d,))
        t.start()
```

执行结果如下：

```python
(MainThread) No value yet
(MainThread) value=999
(Thread-1) No value yet
(Thread-1) value=51
(Thread-2) No value yet
(Thread-2) value=19
```

在digwebs中，你将会看到文件`web.py`里有一句指令是`ctx = threading.local()`，其中ctx就是这样的变量。同样在文件`web.py`里你会看到以下代码用于将请求和响应存储在变量ctx中：

```python
ctx.application = _application
ctx.request = Request(env)
response = ctx.response = Response()
```

## digwebs处理多请求的原理

digwebs处理请求响应的过程分为以下阶段：

1. 构建request
2. 根据request来选择处理函数
3. 处理函数生成响应结果，并返回给请求端

接下来我们深入到代码里看看以上3个阶段的实现。

* 构建request

在文件`web.py`中你会看到以下代码1-1：

```python
class digwebs(object):
    def get_wsgi_application(self):
        _application = Dict(document_root=self.root_path)

        def fn_route():
            def route_entry(context, next):
                def dispatch(i):
                    fn = self.middleware[i][0]
                    if i == len(self.middleware):
                        fn = next
                    return fn(context, lambda: dispatch(i + 1))

                return dispatch(0)

            return route_entry

        fn_exec = fn_route()

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
                if isinstance(r, str):
                    tmp = []
                    tmp.append(r.encode('utf-8'))
                    r = tmp
                if r is None:
                    r = []
                start_response(response.status, response.headers)
                return r
            except RedirectError as e:
                response.set_header('Location', e.location)
                start_response(e.status, response.headers)
                return []
            except HttpError as e:
                start_response(e.status, response.headers)
                return ['<html><body><h1>', e.status, '</h1></body></html>']
            except Exception as e:
                logging.exception(e)
                '''
                if not configs.get('debug',False):
                    start_response('500 Internal Server Error', [])
                    return ['<html><body><h1>500 Internal Server Error</h1></body></html>']
                '''
                exc_type, exc_value, exc_traceback = sys.exc_info()
                fp = StringIO()
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=fp)
                stacks = fp.getvalue()
                fp.close()
                start_response('500 Internal Server Error', [])
                return [
                    r'''<html><body><h1>500 Internal Server Error</h1><div style="font-family:Monaco, Menlo, Consolas, 'Courier New', monospace;"><pre>''',
                    stacks.replace('<', '&lt;').replace('>', '&gt;'),
                    '</pre></div></body></html>'
                ]
            finally:
                del ctx.application
                del ctx.request
                del ctx.response

        return wsgi
```

其中`ctx.request = Request(env)`这句指令就根据原始的请求数据`env`来创建了一个请求变量，该变量的类型是`Request`，`ctx`就是`threading.local()`创建的变量，具有线程数据上下文的特征。

* 根据request来选择处理函数

这句指令`r = fn_exec(ctx, None)`就是根据之前存储的`request`变量来选择处理的函数，处理函数是使用者使用digwebs的6大装饰器自行定义的，比如我们之前定义的函数`list_blogs`：

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

也就是说在函数`list_blogs`中可以获得`ctx`变量，根据该变量就能获得`request`参数，从而根据`request`参数生成不同的响应。

* 处理函数生成响应结果，并返回给请求端

接着看看代码1-1，有以下几句指令：

```python
r = fn_exec(ctx, None)
start_response(response.status, response.headers)
return r
```

当函数`fn_exec`执行完毕之后就会返回响应体，接着通过函数`start_response`将响应的头返回给请求端，其次再将响应体`r`返回给请求端。至此一个完整的请求+响应过程已经完成了，接下来看看现实世界中的服务是如何实现的。

## 基于gunicorn的单线程服务

当你开始提高服务器的吞吐性能时，你会不由自主地将服务运行于一个线程，不会有多线程这一说。由于线程之间的切换会降低服务的性能，因此想要提高服务性能的一种方法就是使用单线程。

问题来了，如果使用单线程，那么`threading.local()`变量就无法区别对待不同的请求响应过程了，那是不是digwebs只能用于多线程的情况？

答案显然是digwebs是可以用单线程启动的，而且保留`ctx`的特性。为了实现这一点，我们需要引入一个框架叫`gunicorn`，其官网在[这里](https://gunicorn.org/)。

通过`gunicorn`你可以以单线程的方式启动使用digwebs编写的服务，这是第一步，那如何保留`ctx`的特性呢？其实当gunicorn启动的时候，它将会把python内置的threading、io等模块替换掉，并引入了协程（coroutine）的概念。coroutine类似于线程，但是当遇到io（程序读写）操作的时候，coroutine将切换到另外一个coroutine执行，所有coroutine都只运行在一个线程下，而替换之后的threading的`threading.local()`类型将针对coroutine。

有了`gunicorn`的帮忙，你会发现你可以将服务以单线程的模式在1个核上运行，当1000个用户同时访问你的服务时，将产生1000个coroutine，这1000个coroutine都会有自己的请求响应，当遇到某个coroutine去执行io操作时，该coroutine将会放弃cpu，其它不需要读写io的coroutine将使用cpu，通过这种方式将大大提高单个服务的吞吐量。如果一台服务器有8核，那么可以启动在这8个核上启动该服务，假设一个服务能够支持1000的并发量，那么8个核就能够支撑8000的并发量。
