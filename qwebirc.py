import cherrypy, os, string, signal, re

favicon = open("static/favicon.ico", "rb").read()

CRETIN_REFERER_PATTERNS = [re.compile(x) for x in [
  r".*alterIWNet.*",
]]

class MainSite(object):
  def is_hg(self):
#    if cherrypy.request.headers.get("Host") != "hg.qwebirc.org":
    return
#
#    if not cherrypy.request.query_string:
#      raise cherrypy.HTTPRedirect("https://bitbucket.org/qwebirc/qwebirc/src/", 301)
#
#    raise cherrypy.HTTPRedirect("https://bitbucket.org/qwebirc/qwebirc/?%s" % cherrypy.request.query_string, 301)

  def __check_referrers(self):
    referer = cherrypy.request.headers.get("Referer")
    if referer is None:
      return

    return any(pattern.match(referer) for pattern in CRETIN_REFERER_PATTERNS)

  @cherrypy.expose
  def index(self, *args, **kwargs):
    self.is_hg()
    if self.__check_referrers():
      return "These aren't the droids you're looking for."
    return self.news()

  def download_file(self, tag, format):
    raise cherrypy.HTTPRedirect("http://hg.qwebirc.org/qwebirc/get/%s.%s" % (tag, format))

  @cherrypy.expose
  def favicon_ico(self):
    #ie doesn't like this...
    #cherrypy.response.headers["Content-Type"] = "image/vnd.microsoft.icon"
    return favicon

def set_downloads(obj):
  for tag in ["default", "stable"]:
    for format in ["gz", "bz2", "zip"]:
      setattr(obj, "download-%s-%s" % (tag, format), (lambda tag=tag, format=format: cherrypy.expose(lambda: obj.download_file(tag, format)))())

def set_templates(obj, pages):
  base = "base.html"
  rootdir = "static"

  base_template = string.Template(open(os.path.join(rootdir, base), "r").read())

  for filename, data in pages.items():
    if isinstance(data, basestring):
      data = dict(title=data)

    content = open(os.path.join(rootdir, "%s.html" % filename), "r").read()
    sub = base_template.safe_substitute(dict(content=content, title=data["title"], page_title=data.get("page_title", data["title"])))
    setattr(obj, filename, (lambda sub=sub: cherrypy.expose(lambda: sub))())

site = MainSite()
def reload():
  set_templates(site, pages={
    "news": dict(title="Welcome!", page_title="News"),
    "features": dict(title="qwebirc's features", page_title="Features"),
    "license": "License",
    "download": "Download",
    "about": "About",
    "faq": "Frequently asked questions",
    "irc": "IRC channel",
    "installation": "Installation",
  })

reload()
set_downloads(site)

signal.signal(signal.SIGUSR2, lambda *args: reload())

cherrypy.tree.mount(site, "/", config="qwebirc.conf")
