from tg import expose, TGController, AppConfig, redirect, request, abort
from configparser import ConfigParser
import unicodedata
import handlers
import webhelpers2
import webhelpers2.text
from web.mtwsgi import make_server
import os
import shutil
import headlights
import printer
import logging

global nextRunTime
global userconfig
global firstrun


def getSubdirectories(dir):
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and name != "__pycache__"]


class SetupController(TGController):
    mainconfig = ConfigParser()

    @expose('web/views/setup/index.xhtml')
    def index(self):
        global firstrun
        if firstrun != True:
            redirect('/')
        return {'firstrun': firstrun}

    @expose('web/views/setup/step1.xhtml')
    def step1(self):
        global firstrun
        if firstrun != True:
            redirect('/')
        return {'firstrun': firstrun}

    @expose()
    def doStep1(self, name, pvend, pprod, escpos=True, eink=False):
        if eink:
            eink = True
        SetupController.mainconfig["General"] = {}
        SetupController.mainconfig["General"]["HelloMyNameIs"] = name
        SetupController.mainconfig["General"]["vendor"] = pvend
        SetupController.mainconfig["General"]["product"] = pprod
        SetupController.mainconfig["Output"]["eink"] = eink
        with open('config/headlights.cfg.tmp', 'w') as headlightscfg:
            SetupController.mainconfig.write(headlightscfg)
        redirect('/setup/step2')

    @expose('web/views/setup/step2.xhtml')
    def step2(self):
        global firstrun
        with open('config/headlights.cfg.tmp', 'r') as headlightscfg:
            confcode = headlightscfg.read()
        if firstrun != True:
            redirect('/')
        return {'firstrun': firstrun, 'confcode': confcode}

    @expose()
    def doStep2(self, scheduleRun):
        SetupController.mainconfig["Schedule"] = {}
        SetupController.mainconfig["Schedule"]["runat"] = scheduleRun
        with open('config/headlights.cfg.tmp', 'w') as headlightscfg:
            SetupController.mainconfig.write(headlightscfg)
        redirect('/setup/step3')

    @expose('web/views/setup/step3.xhtml')
    def step3(self):
        global firstrun
        with open('config/headlights.cfg.tmp', 'r') as headlightscfg:
            confcode = headlightscfg.read()
        if firstrun != True:
            redirect('/')
        return {'firstrun': firstrun, 'confcode': confcode, 'pluginlist': getSubdirectories('plugins')}

    @expose()
    def doStep3(self, pluginSelect):
        SetupController.mainconfig["Plugins"] = {}
        SetupController.mainconfig["Plugins"]["toload"] = str(pluginSelect).strip('[]')
        with open('config/headlights.cfg.tmp', 'w') as headlightscfg:
            SetupController.mainconfig.write(headlightscfg)
        redirect('/setup/finish')

    @expose()
    def finish(self):
        global firstrun
        firstrun = False
        os.remove('config/headlights.cfg.tmp')
        with open('config/headlights.cfg', 'w') as headlightscfg:
            SetupController.mainconfig.write(headlightscfg)
        headlights.reload()
        redirect('/', {'update': 'true'})


class PluginController(TGController):
    mainconfig = ConfigParser()

    @expose('web/views/plugins.xhtml')
    def index(self, enable='', disable='', delete=''):
        def pclass(plugin, enabledlist):
            if plugin in enabledlist:
                return {'class': 'success'}
            else:
                return {'class': 'none'}

        def pHasSettings(plugin):
            pinfo = __import__('plugins.' + plugin, fromlist=[plugin])
            if pinfo.hasconfig == True:
                return {}
            else:
                return {'class': 'disabled',
                        'disabled': 'true'}  # returns disabled to disable the settings icon on the plugins page

        def getplugininfo(plugin):
            pinfo = __import__('plugins.' + plugin, fromlist=[plugin])
            return {'name': pinfo.name,
                    'descrip': pinfo.description,
                    'version': pinfo.version,
                    'author': pinfo.author}

        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        pluginlist = mainconfig['Plugins']['toload'].split(',')
        return {'enabled': pluginlist,
                'all': getSubdirectories('plugins'),
                'pclass': pclass,
                'getpinfo': getplugininfo,
                'enable': enable,
                'disable': disable,
                'delete': delete,
                'psclass': pHasSettings}

    @expose('web/views/pluginsettings.xhtml')
    def settings(self, pname, updated=None):
        pinfo = __import__('plugins.' + pname, fromlist=[pname])
        if pinfo.hasconfig == True:
            plugincfg = ConfigParser()
            try:
                plugincfg.read(pinfo.configfile)
            except PermissionError:
                handlers.criterr(
                    "Permissions error on plugin configuration file. Please ensure you have write permissions for the directory.")
            return {'id': pname,
                    'name': pinfo.name,
                    'hasConfig': True,
                    'configOpts': pinfo.configopts,
                    'currentcfg': plugincfg,
                    'updated': updated}
        else:
            return {'id': pname,
                    'name': pinfo.name,
                    'hasConfig': False,
                    'updated': updated}

    @expose()
    def enablePlugin(self, pid):
        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        pluginlist = mainconfig['Plugins']['toload'].split(',')
        if pluginlist[0] != '':
            pluginlist.append(pid)
        else:
            pluginlist = [pid]
        mainconfig['Plugins']['toload'] = ','.join(pluginlist)
        with open('config/headlights.cfg', 'w') as headlightscfg:
            mainconfig.write(headlightscfg)
        headlights.reload()
        redirect('/plugins', {'enable': 'true'})

    @expose()
    def deletePlugin(self, pid):
        shutil.rmtree('plugins/' + pid)
        headlights.reload()
        redirect('/plugins', {'delete': 'true'})

    @expose()
    def disablePlugin(self, pid):
        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        pluginlist = mainconfig['Plugins']['toload'].split(',')
        pluginlist.remove(pid)
        mainconfig['Plugins']['toload'] = ','.join(pluginlist)
        with open('config/headlights.cfg', 'w') as headlightscfg:
            mainconfig.write(headlightscfg)
        headlights.reload()
        redirect('/plugins', {'disable': 'true'})

    @expose()
    def changeSettings(self, pname, psect, **kw):
        pname = unicodedata.normalize('NFKD', pname).encode('ascii', 'ignore')
        pinfo = __import__('plugins.' + pname, fromlist=[pname])
        if pinfo.hasconfig == True:
            plugincfg = ConfigParser()
            try:
                plugincfg.read(pinfo.configfile)
            except PermissionError:
                handlers.criterr(
                    "Permissions error on plugin configuration file. Please ensure you have write permissions for the directory.")
            for name, value in kw.items():
                plugincfg[psect][name] = value
            with open(pinfo.configfile, 'w') as configfile:
                plugincfg.write(configfile)
            redirect('/plugins/settings/' + pname, {'updated': 'true'})
        else:
            redirect('/plugins/settings/' + pname, {'updated': 'false'})


class RootController(TGController):
    @expose('web/views/index.xhtml')
    def index(self, update='', reload='', run=''):
        global firstrun
        if firstrun == True:
            redirect('/setup/')
        global nextRunTime
        return {'nextRun': nextRunTime, 'update': update, 'reload': reload, 'run': run}

    @expose('web/views/settings.xhtml')
    def settings(self):
        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        return {'runTime': mainconfig["Schedule"]["runat"],
                'name': mainconfig["General"]["HelloMyNameIs"],
                'pvend': mainconfig["General"]["Vendor"],
                'pprod': mainconfig["General"]["Product"]}

    @expose()
    def run(self):
        headlights.start()
        redirect('/', {'run': 'true'})

    @expose()
    def changeTime(self, scheduleRun):
        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        mainconfig["Schedule"]["runat"] = scheduleRun
        with open('config/headlights.cfg', 'w') as headlightscfg:
            mainconfig.write(headlightscfg)
        headlights.reload()
        redirect('/', {'update': 'true'})

    @expose()
    def changeGeneral(self, name, pvend, pprod, escpos=True, eink=False):
        if eink:
            eink = True
        mainconfig = ConfigParser()
        try:
            mainconfig.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        mainconfig["General"]["HelloMyNameIs"] = name
        mainconfig["General"]["vendor"] = pvend
        mainconfig["General"]["product"] = pprod
        mainconfig["Output"]["eink"] = eink
        with open('config/headlights.cfg', 'w') as headlightscfg:
            mainconfig.write(headlightscfg)
        headlights.reload()
        redirect('/', {'update': 'true'})

    @expose()
    def reload(self):
        headlights.reload()
        redirect('/', {'reload': 'true'})

    setup = SetupController()
    plugins = PluginController()


def init(isfirst=False):
    global userconfig
    global nextRunTime
    global firstrun
    firstrun = isfirst
    if os.path.isfile('config/web.cfg') == True:
        userconfig = ConfigParser()
        try:
            userconfig.read('config/web.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on web.cfg. Please ensure you have write permissions for the directory.")
    else:
        print("No configuration file found. Please configure Headlights's server.")
        exit()
    nextRunTime = "loading..."


def run():
    global userconfig
    try:
        port = userconfig['Web']['porttoserve']
    except AttributeError:
        port = '9375'
    global httpd
    config = AppConfig(minimal=True, root_controller=RootController())
    config['helpers'] = webhelpers2
    config.renderers = ['kajiki']
    config.serve_static = True
    config.paths['static_files'] = 'web/public'
    application = config.make_wsgi_app()

    print("Serving on port " + port + "...")
    httpd = make_server('', int(port), application, 3)
    httpd.serve_forever()


def run_api():
    global userconfig
    try:
        port = userconfig['Web']['apiport']
    except KeyError:
        port = '9380'
    global httpd
    config = AppConfig(minimal=True, root_controller=APIRootController())
    config['helpers'] = webhelpers2
    config.renderers = ['kajiki']
    config.serve_static = False
    application = config.make_wsgi_app()

    print("Serving APIs on port " + port + "...")
    httpd = make_server('', int(port), application, 3)
    httpd.serve_forever()


class APIRootController(TGController):
    @expose()
    def tweet_print(self, authkey):
        configfile = ConfigParser()
        try:
            configfile.read('config/headlights.cfg')
        except PermissionError:
            handlers.criterr(
                "Permissions error on headlights.cfg. Please ensure you have write permissions for the directory.")
        maincfg = configfile['General']
        debugcfg = configfile['Debug']

        try:
            key = configfile['Web']['apiauth']
        except KeyError:
            key = ''
        if key != authkey:
            abort(401)
        p = printer.setup_printer(maincfg, debugcfg, logging)
        p.text(request.body)
        p.cut()
        abort(200)


def updateScheduledRun(newtime):
    global nextRunTime
    nextRunTime = newtime


def shutdown():
    global httpd
    httpd.shutdown()
    exit()
