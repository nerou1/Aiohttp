from aiohttp import web
from db import db_context, auth_context
from views import UserView, AdsView
from aiohttp_tokenauth import token_auth_middleware

app = web.Application(
    middlewares=[
        token_auth_middleware(
            auth_context, auth_scheme='Token',
            exclude_routes=('/user', '/ads', )
        )
    ])

app.router.add_routes([
    web.post('/user', UserView),
    web.get('/user/{user_id}', UserView),
    web.post('/ad', AdsView),
    web.patch('/ad/{ad_id}', AdsView),
    web.delete('/ad/{ad_id}', AdsView),
    web.get('/ads', AdsView)
])

app.cleanup_ctx.append(db_context)

web.run_app(app)