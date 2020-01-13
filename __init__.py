# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
"name" : "Gradience",
"author" : "dustractor@gmail.com",
"version" : (1,0),
"blender" : (2, 80, 0),
"location" : "Gradience Tab",
"description" : "Generates sequences of colors in colorramp nodes.",
"warning" : "",
"wiki_url" : "",
"tracker_url" : "",
"category" : "Node Editor"
}

import random
import bpy

from math import modf,sin
from itertools import cycle
from bl_operators.presets import AddPresetBase
from mathutils import Color

def _(f=None,r=[]):
    if not f:
        return r
    r.append(f)
    return f



_k = (
        "g_offs",
        "hue_freq",
        "hue_magn",
        "hue_offs",
        "sat_freq",
        "sat_magn",
        "sat_offs",
        "val_freq",
        "val_magn",
        "val_offs")

def gradience_iter(g,n):
    if not n:
        yield StopIteration
    go = g.g_offs
    hf = g.hue_freq
    hm = g.hue_magn
    ho = g.hue_offs
    sf = g.sat_freq
    sm = g.sat_magn
    so = g.sat_offs
    vf = g.val_freq
    vm = g.val_magn
    vo = g.val_offs
    per = 1.0 / n
    hue,sat,val = g.base_color.hsv
    for i in range(n):
        j = go + (per * i)
        hue += sin((j*hf) + ho) * hm
        sat += sin((j*sf) + so) * sm
        val += sin((j*vf) + vo) * vm
        yield (modf(hue)[0],modf(sat)[0],modf(val)[0])


def update_gradience(self,context):
    gradience = context.screen.gradience
    total = len(gradience.colors)
    for n,k in enumerate(gradience_iter(gradience,total)):
        gradience.colors[n].color.hsv = k


def gradience_controls(layout,gradience):
    row = layout.row(align=True)
    # row.operator("gradience.assign",icon="FORWARD").mode = "MATERIALS"
    # row.operator("gradience.assign",icon="FORWARD").mode = "MATERIALS_UNIQUE"
    # row.operator("gradience.assign",icon="FORWARD").mode = "VERTEX_COLORS"
    row.operator("gradience.to_ramp")
    box = layout.box()
    row = box.row(align=True)
    row.menu("GRADIENCE_MT_preset_menu")
    row.operator("gradience.add_preset",text="",icon="ADD")
    row.operator("gradience.add_preset",text="",icon="REMOVE").remove_active=True
    row = box.row(align=True)
    row.label(icon="BLANK1")
    row.label(text="Hue")
    row.label(text="Saturation")
    row.label(text="Value")
    row = box.row(align=True)
    split = row.split(factor=0.12)
    col = split.column(align=True)
    col.label(text="Freq")
    col.label(text="Magn")
    col.label(text="Offs")
    col = split.column(align=True)
    row = col.row(align=True)
    row.prop(gradience,"hue_freq",text="")
    row.prop(gradience,"hue_magn",text="")
    row.prop(gradience,"hue_offs",text="")
    row = col.row(align=True)
    row.prop(gradience,"sat_freq",text="")
    row.prop(gradience,"sat_magn",text="")
    row.prop(gradience,"sat_offs",text="")
    row = col.row(align=True)
    row.prop(gradience,"val_freq",text="")
    row.prop(gradience,"val_magn",text="")
    row.prop(gradience,"val_offs",text="")
    box.prop(gradience,"g_offs")
    box.operator("gradience.randomize")

def gradience_display(layout,gradience):
    layout.operator("gradience.add",
            text="Colors: %d" % len(gradience.colors),icon="ADD")
    box = layout.box()
    col = box.column(align=True)
    for n,color in enumerate(gradience.colors):
        row = col.row(align=True)
        row.scale_y = 0.8
        row.prop(color,"color",text="")
        row.operator("gradience.del",icon="X",text="",emboss=False).n = n



@_
class GRADIENCE_OT_add(bpy.types.Operator):
    bl_idname = "gradience.add"
    bl_label = "add gradience slot"
    def execute(self,context):
        gradience = context.screen.gradience
        gradience.colors.add()
        update_gradience(None,context)
        return {"FINISHED"}


@_
class GRADIENCE_OT_del(bpy.types.Operator):
    bl_idname = "gradience.del"
    bl_label = "delete gradience slot"
    n: bpy.props.IntProperty()
    def execute(self,context):
        context.screen.gradience.colors.remove(self.n)
        return {"FINISHED"}


@_
class GRADIENCE_OT_assign(bpy.types.Operator):
    bl_idname = "gradience.assign"
    bl_label = "assign  gradience to selected"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    mode: bpy.props.EnumProperty(
            items=[(_,)*3 for _ in (
                "MATERIALS","MATERIALS_UNIQUE","VERTEX_COLORS")],
            default="MATERIALS")
    def execute(self,context):
        gradience = context.screen.gradience
        colorx = cycle([each.color for each in gradience.colors])
        get_color = colorx.__next__


        if self.mode =="VERTEX_COLORS":
            ob = context.object
            me = ob.data
            vcols = me.vertex_colors.active.data
            for vx in vcols:
                vx.color = [*get_color()]+[1.0]
        else:
            if self.mode == "MATERIALS_UNIQUE":
                bpy.ops.object.make_single_user(
                        type="SELECTED_OBJECTS", material=True)
            selected_objects = [
                    ob for ob in context.view_layer.objects.selected
                    if ob.select_get and ob.type in {"LIGHT","MESH","CURVE"}]
            for ob in selected_objects:
                if ob.type in {"CURVE","MESH"}:
                        if not len(ob.data.materials):
                            mat = bpy.data.materials.new("cw_mat")
                            ob.data.materials.append(mat)
                        else:
                            mat = ob.data.materials[0]
                        mat.diffuse_color = [*get_color()] + [1.0]
                elif ob.type == "LAMP":
                    ob.data.color = get_color()
        return {"FINISHED"}


@_
class GRADIENCE_OT_gradience_to_ramp(bpy.types.Operator):
    bl_label = "Ramp"
    bl_idname = "gradience.to_ramp"
    def execute(self,context):
        colors = context.screen.gradience.colors
        colorcount = len(colors)
        if not colorcount:
            return {"CANCELLED"}
        r = context.active_node.color_ramp
        ramp = r.elements
        while len(ramp) > 1:
            ramp.remove(ramp[-1])
        ramp[0].position = 0.0
        ramp[0].color = colors[0].rgba
        inc = 1.0 / (colorcount-1)
        for j in range(1,colorcount):
            n = ramp.new(j*inc)
            n.color=colors[j].rgba
        return {"FINISHED"}


@_
class GRADIENCE_OT_randomize(bpy.types.Operator):
    bl_idname = "gradience.randomize"
    bl_label = "randomize"
    def execute(self,context):
        gradience = context.screen.gradience
        for att in _k:
            setattr(gradience,att,random.random())
        return {"FINISHED"}


@_
class colour(bpy.types.PropertyGroup):
    rgba = property(fget=lambda s:tuple(s.color)+(1.0,))
    color: bpy.props.FloatVectorProperty(min=0.0,max=1.0,subtype="COLOR")


@_
class PaletteProperty(bpy.types.PropertyGroup):
    colors: bpy.props.CollectionProperty(type=colour)


@_
class GradienceProperty(bpy.types.PropertyGroup):
    display: bpy.props.BoolProperty()
    base_color: bpy.props.FloatVectorProperty(
            default=(0.0,0.0,0.0),
            min=0.0,max=1.0,
            precision=7,subtype="COLOR",update=update_gradience)
    colors: bpy.props.CollectionProperty(type=colour)
    defaultd = dict(update=update_gradience,subtype="UNSIGNED",precision=7)
    hue_freq: bpy.props.FloatProperty(default=1.0,**defaultd)
    hue_magn: bpy.props.FloatProperty(default=1.0,**defaultd)
    hue_offs: bpy.props.FloatProperty(default=0.0,**defaultd)
    sat_freq: bpy.props.FloatProperty(default=0.0,**defaultd)
    sat_magn: bpy.props.FloatProperty(default=1.0,**defaultd)
    sat_offs: bpy.props.FloatProperty(default=1.5,**defaultd)
    val_freq: bpy.props.FloatProperty(default=0.0,**defaultd)
    val_magn: bpy.props.FloatProperty(default=1.0,**defaultd)
    val_offs: bpy.props.FloatProperty(default=1.5,**defaultd)
    g_offs: bpy.props.FloatProperty(default=0.0,**defaultd)


@_
class GRADIENCE_MT_preset_menu(bpy.types.Menu):
    bl_label = "Gradience Presets"
    bl_idname= "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset

@_
class GRADIENCE_OT_palette_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_palette_preset"
    bl_label = "add palette preset"
    preset_menu = "GRADIENCE_MT_palette_preset_menu"
    preset_subdir = "gradience_palettes"
    preset_defines = [ "palette = bpy.context.screen.palette" ]
    preset_values = ["palette.colors"]


@_
class GRADIENCE_OT_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_preset"
    bl_label = "add preset"
    preset_menu = "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_defines = [ "gradience = bpy.context.screen.gradience" ]
    preset_values = ["gradience.colors"] + ["gradience.%s" % _ for _ in _k]


@_
class GRADIENCE_PT_gradience(bpy.types.Panel):
    bl_label = "Gradience"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Item"
    bl_options = {"HIDE_HEADER"}
    @classmethod
    def poll(self,context):
        return context.active_node and context.active_node.type == "VALTORGB"
    def draw_header(self,context):
        row = self.layout.row(align=True)
        row.label(icon="COLOR")
    def draw(self,context):
        layout = self.layout
        layout.separator()
        gradience = context.screen.gradience
        gradience_controls(layout,gradience)
        gradience_display(layout,gradience)


def register():
    list(map(bpy.utils.register_class,_()))
    bpy.types.Screen.gradience = bpy.props.PointerProperty(type=GradienceProperty)

def unregister():
    del bpy.types.Screen.gradience
    list(map(bpy.utils.unregister_class,_()))

if __name__ == "__main__":
    register()



