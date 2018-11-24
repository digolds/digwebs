#!/usr/bin/env python

__author__ = 'SLZ'


class Template(object):
    def __init__(self, template_name, **kw):
        '''
        Init a template object with template name, model as dict, and additional kw that will append to model.

        >>> t = Template('hello.html', title='Hello', copyright='@2012')
        >>> t.model['title']
        'Hello'
        >>> t.model['copyright']
        '@2012'
        >>> t = Template('test.html', abc=u'ABC', xyz=u'XYZ')
        >>> t.model['abc']
        u'ABC'
        '''
        self.template_name = template_name
        self.model = dict(**kw)


class TemplateEngine(object):
    '''
    Base template engine.
    '''

    def __call__(self, path, model):
        return '<!-- override this method to render template -->'


class Jinja2TemplateEngine(TemplateEngine):
    '''
    Render using jinja2 template engine.

    >>> templ_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test')
    >>> engine = Jinja2TemplateEngine(templ_path)
    >>> engine.add_filter('datetime', lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'))
    >>> engine('jinja2-test.html', dict(name='Michael', posted_at=datetime.datetime(2014, 6, 1, 10, 11, 12)))
    '<p>Hello, Michael.</p><span>2014-06-01 10:11:12</span>'
    '''

    def __init__(self, templ_dir, **kw):
        from jinja2 import Environment, FileSystemLoader
        if not 'autoescape' in kw:
            kw['autoescape'] = True
        self._env = Environment(
            variable_start_string='{{{{',
            variable_end_string='}}}}',
            loader=FileSystemLoader(templ_dir),
            **kw)

    def add_filter(self, name, fn_filter):
        self._env.filters[name] = fn_filter

    def __call__(self, path, model):
        return self._env.get_template(path).render(**model).encode('utf-8')

if __name__ == '__main__':
    import doctest
    doctest.testmod()