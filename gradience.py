bl_info = {
"name" : "Gradience",
"author" : "dustractor",
"version" : (0, 1),
"blender" : (2, 5, 9),
"api" : 39355,
"location" : "Material",
"description" : "Adds simple functionality for gradient presets (colorbands).",
"warning" : "",
"wiki_url" : "",
"tracker_url" : "",
"category" : "Material"
}

import bpy
from mathutils import Color


class gradient:
    name=None
    label=None
    desc=None
    data=None#tuple(or list) of tuples of 4 floatsorints


t={}

def gradien(f):
    global t
    x=type("GRDT_"+f.__name__, (gradient,),
        {"name": f.__name__, "label": f.__doc__, "desc": f.__doc__,
        "data": f })
    t[f.__name__]=x
    return f

@gradien
def rgb():
    '''red-green-blue'''
    return (
        (1,0,0,1),
        (0,1,0,1),
        (0,0,1,1)
    )

@gradien
def roygbiv():
    '''R O Y G B I V'''
    c=Color()
    C=()
    for i in range(7):
        c.hsv = (i*(1.0/7.0),1.0,1.0)
        C+=((c.r,c.g,c.b,1.0),)
    return C

@gradien
def roygbiv2():
    '''double R O Y G B I V'''
    c=Color()
    C=()
    for i in range(14):
        c.hsv = (i*(1.0/14.0),1.0,1.0)
        C+=((c.r,c.g,c.b,1.0),)
    return C

def apply_(what,what2):
    L=len(what)
    eL=len(what2)
    for j in reversed(range(1,eL)):
        what2.remove(what2[j])
    what2[0].position=0.0
    what2[0].color=what[0]
    for j in range(1,L):
        n=what2.new(j*(1/(L-1)))
        n.color=what[j]
    n.position=1.0

def texcol_(self,context):
    global t
    apply_(t[context.scene.gradience.whicht].data(),context.material.active_texture.color_ramp.elements)

def diff_(self,context):
    global t
    apply_(t[context.scene.gradience.whichd].data(),context.material.diffuse_ramp.elements)

def spec_(self,context):
    global t
    apply_(t[context.scene.gradience.whichs].data(),context.material.specular_ramp.elements)

def gradients_lister(cls,context):
    global t
    return [(a.name,a.label,a.desc) for a in t.values()]

def tog_dif(self,context):
    if context.scene.gradience.indif:
        bpy.types.MATERIAL_PT_diffuse.prepend(ddisp)
    else:
        bpy.types.MATERIAL_PT_diffuse.remove(ddisp)
        
def tog_spec(self,context):
    if context.scene.gradience.inspec:
        bpy.types.MATERIAL_PT_specular.prepend(sdisp)
    else:
        bpy.types.MATERIAL_PT_specular.remove(sdisp)
def tog_tex(self,context):
    if context.scene.gradience.intex:
        bpy.types.TEXTURE_PT_colors.prepend(tdisp)
    else:
        bpy.types.TEXTURE_PT_colors.remove(tdisp)

def tdisp(self,context):
    self.layout.prop(context.scene.gradience,"whicht")

def ddisp(self,context):
    self.layout.prop(context.scene.gradience,"whichd")

def sdisp(self,context):
    self.layout.prop(context.scene.gradience,"whichs")


class gradience(bpy.types.PropertyGroup):   
    indif=bpy.props.BoolProperty(name="diffuse",update=tog_dif)
    inspec=bpy.props.BoolProperty(name="specular",update=tog_spec)
    intex=bpy.props.BoolProperty(name="texture",update=tog_tex)
    whichd=bpy.props.EnumProperty(name="Gradient",items=gradients_lister,update=diff_)
    whichs=bpy.props.EnumProperty(name="Gradient",items=gradients_lister,update=spec_)
    whicht=bpy.props.EnumProperty(name="Gradient",items=gradients_lister,update=texcol_)


class GradientPropertiesPanel(bpy.types.Panel):
    bl_label="Gradient Presets"
    bl_space_type="PROPERTIES"
    bl_region_type="WINDOW"
    bl_context="material"
    def draw(self,context):
        self.layout.prop(context.scene.gradience,"indif")
        self.layout.prop(context.scene.gradience,"inspec")
        self.layout.prop(context.scene.gradience,"intex")


def register():
    bpy.utils.register_class(gradience)
    bpy.types.Scene.gradience=bpy.props.PointerProperty(type=gradience)
    bpy.utils.register_class(GradientPropertiesPanel)

def unregister():
    bpy.utils.unregister_class(GradientPropertiesPanel)
    bpy.utils.unregister_class(gradience)
    del bpy.types.Scene.gradience

if __name__ == "__main__":
    register()
