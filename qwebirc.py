import cherrypy, os, string, signal

favicon = open("static/favicon.ico", "rb").read()

class MainSite(object):
  def is_hg(self):
    if cherrypy.request.headers.get("X-Forwarded-Host") != "hg.qwebirc.org":
      return

    if not cherrypy.request.query_string:
      raise cherrypy.HTTPRedirect("https://bitbucket.org/slug/qwebirc/src/", 301)

    raise cherrypy.HTTPRedirect("https://bitbucket.org/slug/qwebirc/?%s" % cherrypy.request.query_string, 301)

  @cherrypy.expose
  def index(self, *args, **kwargs):
    self.is_hg()
    return self.news()

  def download_file(self, tag, format):
    raise cherrypy.HTTPRedirect("https://bitbucket.org/slug/qwebirc/get/%s.%s" % (tag, format))

  @cherrypy.expose
  def favicon_ico(self):
    #ie doesn't like this...
    #cherrypy.response.headers["Content-Type"] = "image/vnd.microsoft.icon"
    return favicon

def set_downloads(obj):
  for tag in ["default", "stable"]:
    for format in ["gz", "bz2", "zip"]:
      setattr(obj, "download-%s-%s" % (tag, format), (lambda tag=tag, format=format: cherrypy.expose(lambda: obj.download_file(tag, format)))())

def set_templates(obj, **kwargs):
  base = "base.html"
  rootdir = "static"

  base_template = string.Template(open(os.path.join(rootdir, base), "r").read())

  for filename, data in kwargs.items():
    if isinstance(data, basestring):
      data = dict(title=data)

    content = open(os.path.join(rootdir, "%s.html" % filename), "r").read()
    sub = base_template.safe_substitute(dict(content=content, title=data["title"], page_title=data.get("page_title", data["title"])))
    setattr(obj, filename, (lambda sub=sub: cherrypy.expose(lambda: sub))())

site = MainSite()
def reload():
  set_templates(site, news=dict(title="Welcome!", page_title="News"), features=dict(title="qwebirc's features", page_title="Features"), license="License", download="Download", about="About", faq="Frequently asked questions")

reload()
set_downloads(site)

signal.signal(signal.SIGUSR2, lambda *args: reload())

cherrypy.tree.mount(site, "/", config="qwebirc.conf")
