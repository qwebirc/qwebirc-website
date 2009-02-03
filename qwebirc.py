import cherrypy

class MainSite:
  def __init__(self):
    self.data = open("static/index.html", "r").read()

  @cherrypy.expose
  def index(self):
    return self.data

cherrypy.tree.mount(MainSite(), "/", config="qwebirc.conf")
