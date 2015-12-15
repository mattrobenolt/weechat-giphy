import weechat

import json
from urllib import urlencode

cmd_to_query = {}
RED = weechat.color('red')

class Query(object):
    def __init__(self, buf, args):
        self.buf = buf
        self.args = args
        self.out = ''


def hook_process_cb(data, cmd, rc, out, err):
    try:
        query = cmd_to_query[cmd]
    except KeyError:
        return weechat.WEECHAT_RC_ERROR

    if rc > 0 or err:
        try:
            del cmd_to_query[cmd]
        except KeyError:
            pass
        weechat.prnt(query.buf, '[giphy]:\t%soops %r' % (RED, (rc, err),))
        return weechat.WEECHAT_RC_ERROR

    query.out += out

    if rc == -1:
        # We just got a chunk, so keep going
        return weechat.WEECHAT_RC_OK

    try:
        del cmd_to_query[cmd]
    except KeyError:
        pass

    try:
        data = json.loads(query.out)['data'][0]['images']['downsized']['url']
    except (ValueError, KeyError, IndexError) as e:
        weechat.prnt(query.buf, '[giphy]:\t%sNo results found for %r' % (RED, query.args))
        return weechat.WEECHAT_RC_ERROR

    weechat.command(query.buf, '//giphy ' + query.args)
    weechat.command(query.buf, data)
    return weechat.WEECHAT_RC_OK


def giphy_cb(data, buf, args):
    if not args:
        weechat.prnt(buf, '[giphy]:\t%sNothing to search for. :(' % (RED,))
        return weechat.WEECHAT_RC_ERROR
    s_args = args.split()
    if s_args[0][0] == '#':
        weechat.prnt(buf, '[giphy]:\t%sFancy searches aren\'t allowed yet. :(' % (RED,))
        return weechat.WEECHAT_RC_ERROR
    args = ' '.join(s_args)
    cmd = 'url:https://api.giphy.com/v1/gifs/search?' + urlencode({'q': args, 'api_key': 'dc6zaTOxFJmzC', 'limit': 1})
    cmd_to_query[cmd] = Query(buf, args)
    weechat.hook_process(cmd, 10000, 'hook_process_cb', '')
    return weechat.WEECHAT_RC_OK


weechat.register('giphy', 'Matt Robenolt <m@robenolt.com>', '0.0', 'BSD', 'giphy', '', '')
weechat.hook_command('giphy', 'Insert giphy', '[text]', '', '', 'giphy_cb', '')
