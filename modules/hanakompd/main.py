import modules.hanakompd.config as config
import core.lib as lib
import shlex
try:
    import mpd
except:
    print('%s requires mpd. instal it with python3 -m pip install python-mpd2'%__name__)


author = "undefined_value"
name = "HanakoMPD"
description = '''This module allows you to manage MPD, change tracks, volume, stop/resume playback and show current track. '''
version = '0.0.1'
command = '/mpc'

logger = lib.Log('HanakoMPD')


def mpd_query(rq, *args):
    mpc = mpd.MPDClient()
    logger.info('mpc.%s%r'%(rq, args))
    try:
        mpc.connect(config.host, config.port)
        if config.password:
            mpc.password(config.password)
    except ConnectionRefusedError as e:
        logger.warning('mpc.error: %r'%e)
        return False, repr(e)
    except mpd.CommandError as e:
        logger.warning('mpc.error: %r'%e)
        pass
    except Exception as e:
        logger.warning('mpc.error: %r'%e)
        return False, repr(e)
    try:
        response = getattr(mpc, rq)(*args)
        logger.info('mpc.result: %r'%response)
        return True, response
    except Exception as e:
        logger.warning('mpc.error: %r'%e)
        return False, repr(e)


def handle(message, bot):
    params = shlex.split(message.text)
    if len(params) < 2:
        params.append(None)
    _, cmd, *params = params
    if cmd == 'play':
        s, r = mpd_query('play')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        s, r = mpd_query('status')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        if r.get('error'):
            bot.reply_to(message, '<b>ERROR: %s</b>'%r['error'], parse_mode='html')
    elif cmd in ('now', 'current', 'currentsong'):
        s, r = mpd_query('currentsong')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, '''\
<b>Currently playing:</b> <pre>{artist} - {title}</pre>
<b>File:</b> <pre>{file}</pre>'''.format(
    artist=r.get('artist', 'Unknown'),
    title=r.get('title', 'Unknown'),
    file=r.get('file', '--- no data ---')), parse_mode='html')

    elif cmd in ('next', 'nextsong'):
        s, r = mpd_query('next')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        s, r = mpd_query('currentsong')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r.get('file')), parse_mode='html')

    elif cmd in ('prev', 'previous', 'back'):
        s, r = mpd_query('previous')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        s, r = mpd_query('currentsong')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r.get('file')), parse_mode='html')

    elif cmd in ('vol', 'volume', 'setvol'):
        s, r = mpd_query('setvol', params[0])
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        bot.reply_to(message, 'setvol(%s): OK'%params[0])

    elif cmd in ('status'):
        s, r = mpd_query('status')
        if not s:
            bot.reply_to(message, '<pre>%s</pre>'%lib.Utils.htmlescape(r), parse_mode='html')
            return
        output = ''
        for k, v in r.items():
            output += '<b>%s</b>=<code>%r</code>\n'%(k, v)
        bot.reply_to(message, output, parse_mode='html')

    elif cmd == 'query':
        if len(params) < 1:
            bot.reply_to(message, '<b>Not enough arguments</b>', parse_mode='html')
            return
        s, r = mpd_query(params[0], *params[1:])
        if isinstance(r, dict):
            output = ''
            for k, v in r.items():
                output += '<b>%s</b>: <code>%s</code>\n'%(k, lib.Utils.htmlescape(v))
        else:
            output = '<pre>%s</pre>'%lib.Utils.htmlescape(repr(r))
        bot.reply_to(message, output, parse_mode='html')

    elif cmd in ('help', 'man', '?'):
        bot.reply_to(message, '''\
<b>HanakoMPD module by </b><a href="tg://resolve?domain=undefined_value">undefined_value</a>
Commands list:
/mpc next/nextsong -&gt; play next song
/mpc prev/previous/back -&gt; play previous song
/mpv vol/volume/setvol <i>[volume]</i> -&gt; set volume
/mpc now/current/currentsong -&gt; print current song
/mpc status -&gt; print MPD status
/mpc query <i>[command]</i> <i>[..args..]</i>''', parse_mode='html')

    else:
        s, r = mpd_query('status')
        if not s:
            r = {'error': r}
        bot.reply_to(message, '''\
<b>HanakoMPD module by undefined_value</b>
Type /mpc help for more help
Current status: {play_state}
Error level: {error}
Volume: {volume}%'''.format(
    play_state=r.get('state', 'N/A'),
    error=r.get('error', ''),
    volume=r.get('volume', 'N/A')), parse_mode='html')


