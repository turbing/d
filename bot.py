import sqlite3
import discord
from discord.ext import commands
import yaml
import requests
from datetime import datetime
import vk_captchasolver as vc
from bs4 import BeautifulSoup
import aiohttp
import xmltodict
from time import localtime, strftime

conn = sqlite3.connect('xx.db', isolation_level=None, check_same_thread=False)
curs = conn.cursor()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents)
bot.remove_command('h')

config = yaml.safe_load(open('config.yml', 'r').read())

@bot.command()
async def h(ctx):
    await ctx.send('Help:\n:kiss: `h` - help\n:yum: `turb <domain>` — autoclaim\n:eye: `gg <domain>` — remove autoclaimer\n:ghost: `swap <domain> <group token> <user token>` - swapper\n:drop_of_blood: `replace <domain to release> <domain to claim>` - release from group\n:pleading_face: `inv <group domain>` - invite to group\n:imp: `group <group domain> <administrator/moderator/editor/advertiser> <user domain> <is contact (0-1)>` - appoint user as a group manager \n:ok_hand: `l` — autoclaiming list\n:eye: `info <domain>` — whois (group/user)\n:ear: `acc <app> <login> <password>` - access_token generator (Android - 1, iPhone - 2, Windows Desktop - 3, Windows Phone - 4, VK Messenger - 5)')

@bot.command()
async def turb(ctx, url):
    if len(url) >= 5:
        for token in list(open('tokens.txt')):
            if not bool(len(curs.execute('SELECT * FROM `claimlist` WHERE `token` = ?', (token,)).fetchall())):
                try:
                    data = requests.get('https://api.vk.com/method/groups.create', params={
                        'access_token': token,
                        'title': 'lol',
                        'type': 'group',
                        'v': 5.131,
                    }).json()
                    requests.get('https://api.vk.com/method/groups.edit', params={
                        'access_token': token,
                        'group_id': data['response']['id'],
                        'access': 2,
                        'v': 5.131,
                    }).json()
                    requests.get('https://api.vk.com/method/groups.leave', params={
                        'access_token': token,
                        'group_id': data['response']['id'],
                        'v': 5.131 
                    })
                    if data['response']:
                        curs.execute('INSERT INTO `claimlist` (`url`, `gid`, `token`) VALUES (?, ?, ?)', (url, data['response']['id'], token,))
                        await ctx.send(f':yum: Added **{url}** to autoclaimer | GID: `{data["response"]["id"]}`')
                        mambet = requests.get('https://api.vk.com/method/groups.getSuitableInviteLink', params={
                            'access_token': config['vkme_token'],
                            'group_id': data['response']['id'],
                            'v': 5.192,
                        }).json()
                        try:
                            await ctx.send(':yum: Group invite: ' + mambet['response']['url'])
                        except:
                            await ctx.send('```Failed to create group invite:' + mambet['error']['error_msg'] + '```')
                        break
                except:
                    if data['error']:
                        if data['error']['error_code'] == 14:
                            data = requests.get('https://api.vk.com/method/groups.create', params={
                                'access_token': token,
                                'title': 'kek',
                                'type': 'group',
                                'v': 5.131,
                                'captcha_sid': data['error']['captcha_sid'],
                                'captcha_key': vc.solve(sid=data['error']['captcha_sid'], s=1)
                            }).json()
                            requests.get('https://api.vk.com/method/groups.edit', params={
                                'access_token': token,
                                'group_id': data['response']['id'],
                                'access': 2,
                                'v': 5.131,
                            }).json()
                            requests.get('https://api.vk.com/method/groups.leave', params={
                                'access_token': token,
                                'group_id': data['response']['id'],
                                'v': 5.131 
                            })
                            if data['response']:
                                curs.execute('INSERT INTO `claimlist` (`url`, `gid`, `token`) VALUES (?, ?, ?)', (url, data['response']['id'], token,))
                                await ctx.send(f':eye: Added **{url}** to autoclaimer | GID: `{data["response"]["id"]}`')
                                mambet = requests.get('https://api.vk.com/method/groups.getSuitableInviteLink', params={
                                    'access_token': config['vkme_token'],
                                    'group_id': data['response']['id'],
                                    'v': 5.192,
                                }).json()
                                try:
                                    await ctx.send(':eye: Group invite: ' + mambet['response']['url'])
                                except:
                                    await ctx.send('```Failed to create group invite: ' + mambet['error']['error_msg'] + '```')
                                break
                        elif data['error']['error_code'] == 5:
                            with open('tokens.txt', 'r') as file:
                                lines = file.readlines()
                            with open('tokens.txt', 'w') as file:
                                for line in lines:
                                    if line.strip('\n') != f'{token}':
                                        file.write(line)


@bot.command()
async def gg(ctx, url):
    if bool(len(curs.execute('SELECT * FROM `claimlist` WHERE `url` = ?', (url,)).fetchall())):
        curs.execute('DELETE FROM `claimlist` WHERE `url` = ?', (url,))
        await ctx.send(f':yum: Removed **{url}** from autoclaimer')

@bot.command()
async def inv(ctx, url):
    data = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
        'access_token': config['check_token'],
        'screen_name': url,
        'v': 5.192
    }).json()
    mambet = requests.get('https://api.vk.com/method/groups.getSuitableInviteLink', params={
        'access_token': config['vkme_token'],
        'group_id': data['response']['object_id'],
        'v': 5.192,
    }).json()
    try:
        await ctx.send(':yum: Group invite: ' + mambet['response']['url'])
    except:
        await ctx.send('```Failed to create group invite:' + mambet['error']['error_msg'] + '```')

@bot.command()
async def group(ctx, url, level, urll, cont):
    data = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
        'access_token': config['check_token'],
        'screen_name': url,
        'v': 5.131
    }).json()
    datas = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
        'access_token': config['check_token'],
        'screen_name': urll,
        'v': 5.131
    }).json()
    given = requests.get('https://api.vk.com/method/groups.editManager', params={
        'access_token': config['vkme_token'],
        'group_id': data['response']['object_id'],
        'user_id': datas['response']['object_id'],
        'role': level,
        'is_contact': cont,
        'v': 5.192
    }).json()
    if given['response'] == 1:
        await ctx.send(f':yum: {urll} -> {level} in {url}')
    elif given['error']:
        await ctx.send('```Failed, reason: ' + given['error']['error_msg'] + '```')

@bot.command()
async def swap(ctx, domain, grtoken, actoken):
    await ctx.send(f'Currently swapping https://vk.com/{domain}')
    counter = 1
    claimed = 1

    while claimed == 1:
        try:
            data = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
                'access_token': grtoken,
                'screen_name': domain,
                'v': 5.192
            }).json()
            print(f'{strftime("%Y-%m-%d %H:%M:%S", localtime())} {data}')
            dataq = requests.get('https://api.vk.com/method/utils.checkScreenName', params={
                'access_token': actoken,
                'screen_name': domain,
                'v': 5.192
            }).json()
            print(f'{strftime("%Y-%m-%d %H:%M:%S", localtime())} {dataq}')
            if not data['response'] or dataq['response']['status'] == 1:
                datao = requests.get('https://api.vk.com/method/account.saveProfileInfo', params={
                    'access_token': actoken,
                    'screen_name': domain,
                    'v': 5.192
                }).json()
                if datao['response']:
                    await ctx.send(f'@everyone Successfully swapped https://vk.com/{domain}')
                    claimed = 0
                elif not datao['response']:
                    await ctx.send(datao)
        except:
            counter = 2

@bot.command()
async def replace(ctx, url, novoe):
    data = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
        'access_token': config['check_token'],
        'screen_name': url,
        'v': 5.131
    }).json()
    doto = requests.get('https://api.vk.com/method/groups.edit', params={
        'access_token': config['vk_token'],
        'group_id': data['response']['object_id'],
        'screen_name': novoe,
        'v': 5.131,
    }).json()
    if doto['response'] == 1:
        await ctx.send(f':yum: Replaced **{url}** with **{novoe}**')

@bot.command()
async def l(ctx):
    urls = []
    for row in curs.execute('SELECT `url` FROM `claimlist`').fetchall():
        for url in row:
            urls.append(url)
    await ctx.send(urls)

@bot.command()
async def acc(ctx, app, login, password):
    if app == '1':
        data = requests.get(f'https://oauth.vk.com/token?grant_type=password&client_id=2274003&client_secret=hHbZxrka2uZ6jB1inYsH&username={login}&password={password}&v=5.131&2fa_supported=1').json()
        try:
            await ctx.send(data['access_token'])
        except:
            await ctx.send("```" + data['error_description'] + "```")
    elif app == '2':
        data = requests.get(f'https://oauth.vk.com/token?grant_type=password&client_id=3140623&client_secret=VeWdmVclDCtn6ihuP1nt&username={login}&password={password}&v=5.131&2fa_supported=1').json()
        try:
            await ctx.send(data['access_token'])
        except:
            await ctx.send("```" + data['error_description'] + "```")
    elif app == '3':
        data = requests.get(f'https://oauth.vk.com/token?grant_type=password&client_id=3697615&client_secret=AlVXZFMUqyrnABp8ncuU&username={login}&password={password}&v=5.131&2fa_supported=1').json()
        try:
            await ctx.send(data['access_token'])
        except:
            await ctx.send("```" + data['error_description'] + "```")
    elif app == '4':
        data = requests.get(f'https://oauth.vk.com/token?grant_type=password&client_id=3502557&client_secret=PEObAuQi6KloPM4T30DV&username={login}&password={password}&v=5.131&2fa_supported=1').json()
        try:
            await ctx.send(data['access_token'])
        except:
            await ctx.send("```" + data['error_description'] + "```")
    elif app == '5':
        data = requests.get(f'https://oauth.vk.com/token?grant_type=password&client_id=6146827&client_secret=qVxWRF1CwHERuIrKBnqe&username={login}&password={password}&v=5.131&2fa_supported=1').json()
        try:
            await ctx.send(data['access_token'])
        except:
            await ctx.send("```" + data['error_description'] + "```")

@bot.command()
async def info(ctx, url):
    lols = 0
    data = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={
        'access_token': config['check_token'],
        'screen_name': url,
        'v': 5.131
    }).json()
    if not data['response']:
        await ctx.send("Domain does not exist")
    if data['response']['object_id']:
        if data['response']['type'] == 'user':
            x = requests.get('https://api.vk.com/method/users.get', params={
                'access_token': config['vk_token'],
                'user_ids': data['response']['object_id'],
                'fields': 'photo_200,domain',
                'v': 5.131
            }).json()
            actv = int(requests.get("https://api.vk.com/method/messages.getLastActivity?access_token=" + config['vk_token'] + "&user_id=" + str(data['response']['object_id']) + "&v=5.131").json()["response"]["time"])
            actvl = datetime.utcfromtimestamp(actv + (210 * 24 * 60 * 60 + 10800)).strftime('%Y-%m-%d %H:%M:%S')
            actvsl = datetime.utcfromtimestamp(actv + (209 * 24 * 60 * 60 + 10800)).strftime('%Y-%m-%d %H:%M:%S')
            acss = datetime.utcfromtimestamp(actv + 10800).strftime('%Y-%m-%d %H:%M:%S')
            datab = requests.get('http://vk.com/foaf.php?id=' + str(data['response']['object_id']))
            xmls = []
            foafperson = []
            item = []
            yacreated = []
            try:
                xmls = xmltodict.parse(datab.text)
                lols = 0
            except:
                lols = 1
            try:
                foafperson = xmls["rdf:RDF"]["foaf:Person"]
            except:
                lols = 1
            item = foafperson
            try:
                yacreated = item["ya:created"]
                lols = 0
            except:
                datab = requests.get('http://vk.com/foaf.php?id=' + str(data['response']['object_id'] - 1))
                try:
                    xmls = xmltodict.parse(datab.text)
                    lols = 0
                except:
                    lols = 1
                try:
                    foafperson = xmls["rdf:RDF"]["foaf:Person"]
                except:
                    lols = 1
                item = foafperson
                try:
                    yacreated = item["ya:created"]
                    lols = 0
                except:
                    datab = requests.get('http://vk.com/foaf.php?id=' + str(data['response']['object_id'] + 2))
                    try:
                        xmls = xmltodict.parse(datab.text)
                        lols = 0
                    except:
                        lols = 1
                    try:
                        foafperson = xmls["rdf:RDF"]["foaf:Person"]
                    except:
                        lols = 1
                    item = foafperson
                    try:
                        yacreated = item["ya:created"]
                    except:
                        lols = 1
            try:
                hoursy = yacreated["@dc:date"].split("T")[1].split("+")[0]
                rest = yacreated["@dc:date"].split("T")[0]
                yeary = rest.split("-")[0]
                monthy = rest.split("-")[1]
                dayy = rest.split("-")[2]
            except:
                lols = 1
            embed = discord.Embed(title=f'{x["response"][0]["first_name"]} {x["response"][0]["last_name"]}', description=f':eye: https://vk.com/{url}', color=33279)
            embed.set_thumbnail(url=f'{x["response"][0]["photo_200"]}')
            embed.add_field(name='URL', value=f'{x["response"][0]["domain"]}', inline=False)
            embed.add_field(name='User ID', value=f'{data["response"]["object_id"]}', inline=False)
            if lols != 1:
                embed.add_field(name='Created at', value=yeary + "-" + monthy + "-" + dayy + " " + hoursy, inline=False)
            embed.add_field(name='Online', value=acss, inline=False)
            try:
                if x['response'][0]['deactivated'] == 'deleted':
                    embed.add_field(name='Type', value='Deleted', inline=False)
                    embed.add_field(name='Will be deleted at', value=actvl, inline=False)
                    embed.add_field(name='ID release (+ 8-22 hours)', value=actvsl, inline=False)
                elif x['response'][0]['deactivated'] == 'banned':
                    embed.add_field(name='Type', value='Banned/Freeze', inline=False)
            except:
                if x['response'][0]['is_closed'] == 0:
                    embed.add_field(name='Type', value='Public', inline=False)
                elif x['response'][0]['is_closed'] == 1:
                    embed.add_field(name='Type', value='Private', inline=False)
            await ctx.send(embed=embed)
        elif data['response']['type'] == 'group':
            x = requests.get('https://api.vk.com/method/groups.getById', params={
                'access_token': config['check_token'],
                'group_id': data['response']['object_id'],
                'v': 5.131
            }).json()
            datab = requests.get('http://vk.com/foaf.php?id=-' + str(data['response']['object_id']))
            xmls = []
            foafperson = []
            item = []
            try:
                xmls = xmltodict.parse(datab.text)
                lols = 0
            except:
                lols = 1
            try:
                foafgroup = xmls["rdf:RDF"]["foaf:Group"]
            except:
                lols = 1
            item = foafgroup
            try:
                memberscount = item["ya:membersCount"]
                lols = 0
            except:
                lols = 1
            embed = discord.Embed(title=f'{x["response"][0]["name"]}', description=f':eye: https://vk.com/{url}', color=33279)
            embed.set_thumbnail(url=f'{x["response"][0]["photo_200"]}')
            embed.add_field(name='URL', value=f'{x["response"][0]["screen_name"]}', inline=False)
            embed.add_field(name="Group ID", value=f'{data["response"]["object_id"]}', inline=False)
            if lols != 1:
                embed.add_field(name="Members count", value=memberscount, inline=False)
            try:
                if x['response'][0]['deactivated'] == 'banned':
                    embed.add_field(name='Type', value='Banned', inline=False)
            except:
                if x['response'][0]['is_closed'] == 0:
                    embed.add_field(name='Type', value='Open', inline=False)
                elif x['response'][0]['is_closed'] == 1:
                    embed.add_field(name='Type', value='Closed', inline=False)
                elif x['response'][0]['is_closed'] == 2:
                    embed.add_field(name='Type', value='Private', inline=False)
            await ctx.send(embed=embed)

bot.run(config['dc_token'])
