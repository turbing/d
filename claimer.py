import sqlite3
import asyncio
import aiohttp
import webhook
import yaml
from discord.ext import commands

conn = sqlite3.connect('xx.db', isolation_level=None, check_same_thread=False)
curs = conn.cursor()
cfgs = yaml.safe_load(open('config.yml', 'r').read())

async def claim(session, url, gid, token, **kwargs):
    resp = await session.request('GET', url=f'https://api.vk.com/method/utils.checkScreenName?screen_name={url}&access_token={token}&v=5.131', **kwargs)
    data = await resp.json()
    print(data)
    gaz = await session.request('GET', url=f'https://api.vk.com/method/utils.resolveScreenName?screen_name={url}&access_token=' + cfgs['turbo_token'] + '&v=5.131', **kwargs)
    gazd = await gaz.json()
    print(gazd)
    try:
        if data['response']['status'] == 1 or gazd['response']['object_id'] == None:
            respo = await session.request('GET', url=f'https://api.vk.com/method/groups.edit?group_id={gid}&screen_name={url}&access_token={token}&v=5.131', **kwargs)
            datao = await respo.json()
            print(datao)
            if datao['response'] == 1:
                curs.execute('DELETE FROM `claimlist` WHERE `url` = ?', (url,))
                webhook.embed('Autoclaimed URL', f'Successfully autoclaimed {url}', 3066993)
                webhook.message(f'@everyone {url}: {gid}, {token}')
                webhook.message('https://cdn.discordapp.com/attachments/992383996111626360/1003253415058616320/Bouncing.webm')
                webhook.message(f'w {url}')
                return datao
    except:
        if data['error']['error_code'] == None:
            with open('tokens.txt', 'r') as file:
                lines = file.readlines()
            with open('tokens.txt', 'w') as file:
                for line in lines:
                    if line.strip('\n') != f'{token}':
                        file.write(line)
            conn.execute('DELETE FROM `claimlist` WHERE `token` = ?', (token,))
            return data

async def main(**kwargs):
    while True:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in conn.execute("SELECT * FROM `claimlist`").fetchall():
                await asyncio.sleep(0.2)
                tasks.append(claim(session=session, url=url[0], gid=url[1], token=url[2], **kwargs))
            await asyncio.gather(*tasks, return_exceptions=True)

asyncio.ensure_future(main())

loop = asyncio.get_event_loop()
loop.run_forever()
