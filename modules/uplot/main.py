import modules.uplot.config as config
import core.lib as lib
from PIL import Image, ImageDraw, ImageFont
import os
import math as _math
from zlib import crc32

author = "undefined_value"
name = "UPlot module"
description = '''This module allows you to plot math functions. '''
version = '0.0.1'
command = '/plot'

logger = lib.Log('UPlot')


def null_func(name):
    def null_func(*args, **kwargs):
        pass
    return null_func


namespace = {
        k: getattr(_math, k)
        for k in dir(_math)
        if not k.startswith('_')
        }
namespace['tg'] = lambda angle: _math.sin(angle) / _math.cos(angle)
namespace['ctg'] = lambda angle: _math.cos(angle) / _math.sin(angle)
namespace['__import__'] = null_func('__import__')
namespace['dir'] = null_func('dir')
namespace['quit'] = null_func('quit')
namespace['__name__'] = author
namespace['__loader__'] = author
namespace['exit'] = null_func('exit')


def calcvalues(func):
    datasets = [[]]
    for i in range(-config.sizes['width'] // 2, config.sizes['width'] // 2 + 1):
        x = i / config.sizes['step']
        try:
            ns = namespace.copy()
            ns['x'] = x
            y = eval(func, ns, ns)
            datasets[-1].append((x, y,),)
        except Exception:
            datasets.append([])
    return datasets


def gc2ic(xy):
    ix = config.sizes['step'] * xy[0] + config.sizes['width'] // 2
    iy = config.sizes['height'] // 2 - config.sizes['step'] * xy[1]
    return ix, iy


def handle(message, bot):
    logger.info('user %d started plotting %r'%(message.from_user.id, message.text))
    im = Image.new('RGB', (config.sizes['width'], config.sizes['height']), config.colors['background'])
    dr = ImageDraw.Draw(im)

    for x in range(0, config.sizes['height'], config.sizes['step']):
        dr.line((0, x, config.sizes['width'], x),
                fill=config.colors['grid'], width=config.sizes['gridwidth'])
    for y in range(0, config.sizes['width'], config.sizes['step']):
        dr.line((y, 0, y, config.sizes['height']),
                fill=config.colors['grid'], width=config.sizes['gridwidth'])

    dr.line((0, config.sizes['height'] // 2, config.sizes['width'], config.sizes['height'] // 2),
            fill=config.colors['axis'], width=config.sizes['axiswidth'])
    dr.line((config.sizes['width'] // 2, 0, config.sizes['width'] // 2, config.sizes['height']),
            fill=config.colors['axis'], width=config.sizes['axiswidth'])
            
    func = ' '.join(message.text.split(' ')[1:])
    for ds in calcvalues(func):
        ln = [gc2ic(pnt) for pnt in ds]
        dr.line(ln, fill=config.colors['curve'], width=config.sizes['curvewidth'])

    name = 'tmp-draw%d.png'%crc32(func.encode())
    im.save(name)
    bot.send_photo(message.chat.id,
            open(name, 'rb'),
            caption='<pre>y = %s</pre>'%lib.Utils.htmlescape(func),
            parse_mode='html',
            reply_to_message_id=message.message_id)
    os.remove(name)


