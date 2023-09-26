import json

from aiohttp import web
from db import Users, Ads
import aiohttp_sqlalchemy as ahsa
from sqlalchemy import select, update
from uuid import uuid5, NAMESPACE_OID
from datetime import datetime

class UserView(web.View, ahsa.SAMixin):
    async def get(self):
        user_id = self.request.match_info['user_id']
        db_session = self.get_sa_session()
        user = await db_session.execute(select(Users).where(Users.id == int(user_id)))
        user = user.fetchone()
        if not user:
            response = (
                {
                    'error': 'User not found'
                }
            )
            return web.json_response(response)
        user = user[0]
        return web.json_response(
            {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        )

    async def post(self):
        db_session = self.get_sa_session()
        user_data = await self.request.json()
        user_data['password'] = str(uuid5(NAMESPACE_OID, user_data.get('name')))
        new_user = Users(**user_data)
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return web.json_response({
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'token': new_user.password
        })


class AdsView(web.View, ahsa.SAMixin):
    async def auth(self, request):
        token = request.headers.get("Authorization")[6:]
        db_session = self.get_sa_session()
        user = await db_session.execute(select(Users).where(Users.password == token))
        user = user.fetchone()
        return user


    async def get(self):
        ads = []
        db_session = self.get_sa_session()
        ads_res = await db_session.execute(select(Ads))
        ads_res = ads_res.fetchall()
        for ad in ads_res:
            ad = ad[0]
            ads.append({
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'adv_date': str(ad.adv_date),
                'user_id': ad.user_id
            })
        return web.json_response(ads)

    async def post(self):
        ad_data = await self.request.json()
        db_session = self.get_sa_session()
        user = await self.auth(self.request)
        if not user:
            return web.json_response({
                'error': 'Unauthorized'
            })
        else:
            user = user[0]
            ad_data['user_id'] = user.id
            ad_data['adv_date'] = datetime.now()
            new_ad = Ads(**ad_data)
            db_session.add(new_ad)
            await db_session.commit()
            await db_session.refresh(new_ad)
            return web.json_response({
                'id': new_ad.id,
                'title': new_ad.title,
                'description': new_ad.description,
                'adv_date': str(new_ad.adv_date),
                'user_id': new_ad.user_id
            })

    async def delete(self):
        ad_id = self.request.match_info['ad_id']
        db_session = self.get_sa_session()
        user = await self.auth(self.request)
        if not user:
            return web.json_response({
                'error': 'Unauthorized'
            })
        else:
            user = user[0]
        ad = await db_session.execute(select(Ads).where(Ads.id == ad_id))
        ad = ad.fetchone()
        if not ad:
            return web.json_response({
                'error': 'Not found'
            })
        else:
            ad = ad[0]
        if ad.user_id != user.id:
            return web.json_response({
                'error': 'Unauthorized'
            })
        await db_session.delete(ad)
        await db_session.commit()
        return web.json_response({
            'status': 'removed',
            'ad_id': ad_id
        })

    async def patch(self):
        ad_id = self.request.match_info['ad_id']
        db_session = self.get_sa_session()
        user = await self.auth(self.request)
        if not user:
            return web.json_response({
                'error': 'Unauthorized'
            })
        else:
            user = user[0]
        ad = await db_session.execute(select(Ads).where(Ads.id == ad_id))
        ad = ad.fetchone()
        if not ad:
            return web.json_response({
                'error': 'Not found'
            })
        else:
            ad = ad[0]
        if ad.user_id != user.id:
            return web.json_response({
                'error': 'Unauthorized'
            })
        ad_data = await self.request.json()
        ad_data['user_id'] = user.id
        ad_data['adv_date'] = datetime.now()
        statement = update(Ads).where(Ads.id == ad.id).values(**ad_data)
        await db_session.execute(statement)
        await db_session.commit()
        await db_session.refresh(ad)
        return web.json_response({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'adv_date': str(ad.adv_date),
            'user_id': ad.user_id
        })