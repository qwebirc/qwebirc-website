import web
import re

#web.config.debug = True

PAGES = dict((k, v if isinstance(v, dict) else dict(title=v, page_title=v)) for k, v in {
  "news": dict(title="Welcome!", page_title="News"),
  "features": dict(title="qwebirc's features", page_title="Features"),
  "license": "License",
  "download": "Download",
  "about": "About",
  "faq": "Frequently asked questions",
  "irc": "IRC channel",
  "installation": "Installation",
}.items())

CRETIN_REFERRER_PATTERNS = [re.compile(x) for x in (
  r"alterIWNet",
)]

render = web.template.render('templates/')

def check_referrer(fn):
  def decorator(*args, **kwargs):
    referrer = web.ctx.env.get("HTTP_REFERER")
    if referrer is not None and any(x.search(referrer) for x in CRETIN_REFERRER_PATTERNS):
      return "these aren't the droids you're looking for"
    return fn(*args, **kwargs)

  return decorator

class default(object):
  @check_referrer
  def GET(self, path):
    if not path:
      path = "news"

    return render.base(content=getattr(render, path)(), **PAGES[path])

class download(object):
  def GET(self, tag, format):
    web.redirect("https://github.com/qwebirc/qwebirc/archive/%s.%s" % (tag, format))

urls = reduce(lambda x, y: x+y, (("^/(%s)$" % k, "default") for k in PAGES)) + (
  "^/()$", "default"
)

for tag in "master", "stable":
  for format in "zip",:
    urls += ("^/download-(%s)-(%s)$" % (tag, format), "download")

app = web.application(urls, globals(), autoreload=True)

if __name__ == "__main__":
  app.run()

