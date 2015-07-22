import sys
import plone.recipe.zope2instance.ctl

sys.exit(plone.recipe.zope2instance.ctl.main(
    ['-C', 'parts/instance/etc/zope.conf']
    + sys.argv[1:]
))
