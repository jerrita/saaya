# saaya 通知板

from saaya.session import Bot
from saaya.utils import PluginManager
from saaya.logger import logger

from sanic import Sanic, Request
from sanic.response import text

session: Bot
app = Sanic(__name__)


@app.route("/notice")
async def notice(req: Request):
    parm = req.args

    notes = 'None' if 'notice' not in parm else parm['notice'][0]
    title = 'No Title' if 'title' not in parm else parm['title'][0]

    logger.info(f'Receive notice [{title}]: {notes}')

    msg = [title, '\n--------------------------\n', notes]

    res = ['OK.']

    if 'group' in parm:
        num = int(parm['group'][0])
        session.sendGroupMessage(num, msg)
        res.append(f'Group message at {num} sent.')

    if 'qq' in parm:
        num = int(parm['qq'][0])
        session.sendFriendMessage(num, msg)
        res.append(f'Friend message at {num} sent.')

    return text('\n'.join(res))


@PluginManager.registerEvent('OnLoad')
def notice(bot: Bot):
    global session
    session = bot
    logger.info('Starting notice board...')
    app.run(host='0.0.0.0', port=31284)
