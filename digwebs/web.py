from aiohttp import web

if __name__ == '__main__':
    #in debug mode
    app = web.Application()
    web.run_app(app,host='127.0.0.1',port=8080)
else:
    #in production mode
    app = web.Application()

