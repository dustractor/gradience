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
"version" : (0, 7),
"blender" : (2, 6, 9),
"api" : 61000,
"location" : "Gradience Tab",
"description" : "Generate sequence of colors and apply to ramp or selected object materials.",
"warning" : "",
"wiki_url" : "",
"tracker_url" : "",
"category" : "Material"
}

import bpy
from bl_operators.presets import AddPresetBase
from mathutils import Color
from math import modf,sin
import random
from itertools import cycle


_k = "global_offset hue_freq hue_magn hue_offs sat_freq sat_magn sat_offs val_freq val_magn val_offs".split()


def update_gradience(self,context):
    if not context.active_object:
        return
    gradience = context.active_object.gradience
    gl,hf,hm,ho,sf,sm,so,vf,vm,vo = gradience.global_offset,gradience.hue_freq, gradience.hue_magn, gradience.hue_offs, gradience.sat_freq, gradience.sat_magn, gradience.sat_offs, gradience.val_freq, gradience.val_magn, gradience.val_offs
    tot = len(gradience.colors)
    if not tot:
        return
    per = 1.0 / tot
    hue,sat,val = gradience.base_color.hsv
    for n in range(tot):
        i = gl +(per * n)
        hue += sin((i*hf) + ho) * hm
        sat += sin((i*sf) + so) * sm
        val += sin((i*vf) + vo) * vm
        gradience.colors[n].color.hsv = (modf(hue)[0],modf(sat)[0],modf(val)[0])

def gradience_controls(layout,gradience):
    row = layout.row(align=True)
    row.operator('gradience.assign',icon='FORWARD',text='')
    row.operator("gradience.to_ramp")
    box = layout.box()
    row = box.row(align=True)
    row.menu("GRADIENCE_MT_preset_menu")
    row.operator("gradience.add_preset",text="",icon="ZOOMIN")
    row.operator("gradience.add_preset",text="",icon="ZOOMOUT").remove_active=True
    row = box.row(align=True)
    row.label(icon="BLANK1")
    row.label('Hue')
    row.label('Saturation')
    row.label('Value')
    row = box.row(align=True)
    split = row.split(percentage=0.1)
    col = split.column(align=True)
    col.label("Freq")
    col.label("Magn")
    col.label("Offs")
    col = split.column(align=True)
    row = col.row(align=True)
    row.prop(gradience,'hue_freq',text='')
    row.prop(gradience,'hue_magn',text='')
    row.prop(gradience,'hue_offs',text='')
    row = col.row(align=True)
    row.prop(gradience,'sat_freq',text='')
    row.prop(gradience,'sat_magn',text='')
    row.prop(gradience,'sat_offs',text='')
    row = col.row(align=True)
    row.prop(gradience,'val_freq',text='')
    row.prop(gradience,'val_magn',text='')
    row.prop(gradience,'val_offs',text='')

    box.prop(gradience,'global_offset')
    box.operator("gradience.randomize")

def gradience_display(layout,gradience):
    layout.operator("gradience.add",text="Colors: %d" % len(gradience.colors),icon="ZOOMIN")
    col = layout.column(align=True)
    col.scale_y = 0.8
    col.scale_x = 0.8
    for n,color in enumerate(gradience.colors):
        row = col.row(align=True)
        row.prop(color,'color',text='')
        row.operator('gradience.del',icon='X',text='',emboss=False).n = n
    layout.operator("gradience.to_palette")

def palette_display(layout,palette):
    for color in palette.colors:
        layout.prop(color,"color",text="")
    box = layout.box()
    row = box.row(align=True)
    row.menu("GRADIENCE_MT_palette_preset_menu")
    row.operator("gradience.add_palette_preset",text="",icon="ZOOMIN")
    row.operator("gradience.add_palette_preset",text="",icon="ZOOMOUT").remove_active=True


class colour(bpy.types.PropertyGroup):
    rgba = property(fget=lambda s:tuple(s.color)+(1.0,))
    color = bpy.props.FloatVectorProperty(min=0.0,max=1.0,subtype="COLOR")


class PaletteProperty(bpy.types.PropertyGroup):
    colors = bpy.props.CollectionProperty(type=colour)


class GradienceProperty(bpy.types.PropertyGroup):
    display = bpy.props.BoolProperty()
    base_color = bpy.props.FloatVectorProperty(default=(0.0,0.0,0.0),min=0.0,max=1.0,precision=7,subtype="COLOR",update=update_gradience)
    colors = bpy.props.CollectionProperty(type=colour)
    hue_freq = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED',precision=7)
    hue_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED',precision=7)
    hue_offs = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED',precision=7)
    sat_freq = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED',precision=7)
    sat_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED',precision=7)
    sat_offs = bpy.props.FloatProperty(update=update_gradience,default=1.5,subtype='UNSIGNED',precision=7)
    val_freq = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED',precision=7)
    val_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED',precision=7)
    val_offs = bpy.props.FloatProperty(update=update_gradience,default=1.5,subtype='UNSIGNED',precision=7)
    global_offset = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED',precision=7)


class GRADIENCE_OT_to_palette(bpy.types.Operator):
    bl_idname = "gradience.to_palette"
    bl_label = "gradience to palette"
    def execute(self,context):
        gradience = context.active_object.gradience
        palette = context.active_object.palette
        while len(palette.colors) > len(gradience.colors):
            palette.colors.remove(palette.colors[-1])
        while len(palette.colors) < len(gradience.colors):
            palette.colors.add()
        for g,p in zip(gradience.colors,palette.colors):
            p.color = g.color
        return {"FINISHED"}


class GRADIENCE_OT_add(bpy.types.Operator):
    bl_idname = "gradience.add"
    bl_label = "add gradience slot"
    def execute(self,context):
        gradience = context.active_object.gradience
        gradience.colors.add()
        update_gradience(None,context)
        return {"FINISHED"}


class GRADIENCE_OT_del(bpy.types.Operator):
    bl_idname = "gradience.del"
    bl_label = "delete gradience slot"
    n = bpy.props.IntProperty()
    def execute(self,context):
        context.active_object.gradience.colors.remove(self.n)
        return {"FINISHED"}


class GRADIENCE_OT_assign(bpy.types.Operator):
    bl_idname = "gradience.assign"
    bl_label = "assign  gradience to selected"
    n = bpy.props.IntProperty(min=-1,default=-1)
    single_ize = bpy.props.BoolProperty()
    vcols = bpy.props.BoolProperty()
    def invoke(self,context,event):
        self.single_ize = event.shift
        self.vcols = event.alt
        return self.execute(context)
    def execute(self,context):
        gradience = context.active_object.gradience
        if self.single_ize:
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', material=True)
        colorx = cycle([each.color for each in gradience.colors])
        get_color = colorx.__next__
        if self.vcols:
            ob = context.object
            me = ob.data
            vcols = me.vertex_colors.active.data
            for vx in vcols:
                c = get_color()
                vx.color = (c[0],c[1],c[2])
        else:
            selected_objects = [ob for ob in bpy.data.objects if ob.select and ob.type in {'LAMP','MESH','CURVE'}]
            for ob in selected_objects:
                if ob.type in {'CURVE','MESH'}:
                        if not len(ob.data.materials):
                            mat = bpy.data.materials.new('cw_mat')
                            ob.data.materials.append(mat)
                        else:
                            mat = ob.data.materials[0]
                        mat.diffuse_color = get_color()
                elif ob.type == 'LAMP':
                    ob.data.color = get_color()
        return {"FINISHED"}


class GRADIENCE_OT_gradience_to_ramp(bpy.types.Operator):
    bl_label = "Ramp"
    bl_idname = "gradience.to_ramp"
    constant = bpy.props.BoolProperty()
    def invoke(self,context,event):
        self.constant = event.shift or event.alt or event.oskey or event.ctrl
        return self.execute(context)
    def execute(self,context):
        colors = context.active_object.gradience.colors
        colorcount = len(colors)
        if not colorcount:
            return {"CANCELLED"}
        r = None
        mat = context.active_object.data.materials[0]
        mat.use_diffuse_ramp = True
        r = mat.diffuse_ramp
        if self.constant:
            r.interpolation = "CONSTANT"
        ramp = r.elements
        while len(ramp) > 1:
            ramp.remove(ramp[-1])
        ramp[0].position = 0.0
        ramp[0].color = colors[0].rgba
        inc = 1.0 / (colorcount-1)
        for j in range(1,colorcount):
            n=ramp.new(j*inc)
            n.color=colors[j].rgba
        return {"FINISHED"}


class GRADIENCE_OT_randomize(bpy.types.Operator):
    bl_idname = "gradience.randomize"
    bl_label = "randomize"
    def execute(self,context):
        gradience = context.active_object.gradience
        for att in _k:
            setattr(gradience,att,random.random())
        return {"FINISHED"}


class GRADIENCE_MT_preset_menu(bpy.types.Menu):
    bl_label = "Gradience Palettes"
    bl_idname= "GRADIENCE_MT_palette_preset_menu"
    preset_subdir = "gradience_palettes"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class GRADIENCE_MT_preset_menu(bpy.types.Menu):
    bl_label = "Gradience Presets"
    bl_idname= "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_operator = "script.execute_preset"
    draw = bpy.types.Menu.draw_preset


class GRADIENCE_OT_palette_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_palette_preset"
    bl_label = "add palette preset"
    preset_menu = "GRADIENCE_MT_palette_preset_menu"
    preset_subdir = "gradience_palettes"
    preset_defines = [ "palette = bpy.context.active_object.palette" ]
    preset_values = ["palette.colors"]


class GRADIENCE_OT_preset_add(AddPresetBase,bpy.types.Operator):
    bl_idname = "gradience.add_preset"
    bl_label = "add preset"
    preset_menu = "GRADIENCE_MT_preset_menu"
    preset_subdir = "gradience"
    preset_defines = [ "gradience = bpy.context.active_object.gradience" ]
    preset_values = ["gradience.colors"] + ["gradience.%s" % _ for _ in _k]


class GRADIENCE_PT_gradience(bpy.types.Panel):
    bl_label = "Gradience"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Gradience"
    def draw_header(self,context):
        row = self.layout.row(align=True)
        row.label(icon="COLOR")
    def draw(self,context):
        gradience = context.active_object.gradience
        palette = context.active_object.palette
        layout = self.layout
        gradience_controls(layout,gradience)
        layout.separator()
        gradience_display(layout,gradience)
        palette_display(layout,palette)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.gradience = bpy.props.PointerProperty(type=GradienceProperty)
    bpy.types.Object.palette = bpy.props.PointerProperty(type=PaletteProperty)

def unregister():
    del bpy.types.Object.gradience
    del bpy.types.Object.palette
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()



