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
"author" : "dustractor",
"version" : (0, 1),
"blender" : (2, 6, 9),
"api" : 61000,
"location" : "Material",
"description" : "Generate sequence of colors and apply to ramp or selected object materials.",
"warning" : "",
"wiki_url" : "",
"tracker_url" : "",
"category" : "Material"
}
import bpy
from mathutils import Color
from math import modf,sin
import random
from itertools import cycle



def update_gradience(self,context):
    if not context.active_object:
        return
    wheel = context.active_object.gradience
    hf,hm,ho,sf,sm,so,vf,vm,vo = wheel.hue_mod_freq, wheel.hue_mod_magn, wheel.hue_mod_offs, wheel.sat_mod_freq, wheel.sat_mod_magn, wheel.sat_mod_offs, wheel.val_mod_freq, wheel.val_mod_magn, wheel.val_mod_offs
    gl = wheel.global_offset
    tot = len(wheel.colors)
    per = 1.0 / tot
    hue,sat,val = wheel.base_color.hsv
    for n in range(tot):
        i = gl +(per * n)
        hue += sin((i*hf) + ho) * hm
        sat += sin((i*sf) + so) * sm
        val += sin((i*vf) + vo) * vm
        wheel.colors[n].color.hsv = (modf(hue)[0],modf(sat)[0],modf(val)[0])


class colour(bpy.types.PropertyGroup):
    rgba = property(fget=lambda s:tuple(s.color)+(1.0,))
    color = bpy.props.FloatVectorProperty(min=0.0,max=1.0,subtype="COLOR")


class ChromatonicProp(bpy.types.PropertyGroup):
    display = bpy.props.BoolProperty()
    show_params = bpy.props.BoolProperty()
    base_color = bpy.props.FloatVectorProperty(default=(0.0,0.0,0.0),min=0.0,max=1.0,precision=7,subtype="COLOR",update=update_gradience)
    colors = bpy.props.CollectionProperty(type=colour)
    hue_mod_freq = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED')
    hue_mod_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED')
    hue_mod_offs = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED')
    sat_mod_freq = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED')
    sat_mod_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED')
    sat_mod_offs = bpy.props.FloatProperty(update=update_gradience,default=1.5,subtype='UNSIGNED')
    val_mod_freq = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED')
    val_mod_magn = bpy.props.FloatProperty(update=update_gradience,default=1.0,subtype='UNSIGNED')
    val_mod_offs = bpy.props.FloatProperty(update=update_gradience,default=1.5,subtype='UNSIGNED')
    global_offset = bpy.props.FloatProperty(update=update_gradience,default=0.0,subtype='UNSIGNED')


class GRADIENCE_OT_add(bpy.types.Operator):
    bl_idname = "gradience.add"
    bl_label = "add gradience slot"
    def execute(self,context):
        wheel = context.active_object.gradience.colors
        wheel.add()
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
        wheel = context.active_object.gradience
        if self.single_ize:
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', material=True)
        colorx = cycle([each.color for each in wheel.colors])
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
        cl = len(colors)
        if not len(colors):
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
        inc = 1.0 / (cl-1)
        for j in range(1,cl):
            n=ramp.new(j*inc)
            n.color=colors[j].rgba
        return {"FINISHED"}


class GRADIENCE_OT_randomize(bpy.types.Operator):
    bl_idname = "gradience.randomize"
    bl_label = "randomize"
    def execute(self,context):
        wheel = context.active_object.gradience
        for att in ("hue_mod_freq","hue_mod_magn","hue_mod_offs","sat_mod_freq","sat_mod_magn","sat_mod_offs","val_mod_freq","val_mod_magn","val_mod_offs"):
            setattr(wheel,att,random.random())
        return {"FINISHED"}

def gradience_controls(layout,wheel):
    row = layout.row(align=True)
    row.operator('gradience.assign',icon='FORWARD',text='')
    row.operator("gradience.to_ramp")
    row.prop(wheel,"show_params",toggle=True,icon=["DISCLOSURE_TRI_RIGHT_VEC","DISCLOSURE_TRI_DOWN_VEC"][wheel.show_params])
    if wheel.show_params:
        row = layout.row(align=True)
        row.prop(wheel,'base_color')
        split = layout.split()
        d,a,b,c = split.column(align=True),split.column(align=True),split.column(align=True),split.column(align=True)
        d.label('Mod')
        d.label('Freq')
        d.label('Mag')
        d.label('Off')
        a.label('Hue')
        a.prop(wheel,'hue_mod_freq',text='')
        a.prop(wheel,'hue_mod_magn',text='')
        a.prop(wheel,'hue_mod_offs',text='')
        b.label('Saturation')
        b.prop(wheel,'sat_mod_freq',text='')
        b.prop(wheel,'sat_mod_magn',text='')
        b.prop(wheel,'sat_mod_offs',text='')
        c.label('Value')
        c.prop(wheel,'val_mod_freq',text='')
        c.prop(wheel,'val_mod_magn',text='')
        c.prop(wheel,'val_mod_offs',text='')
        layout.prop(wheel,'global_offset')
    layout.operator("gradience.randomize")

def gradience_display(layout,wheel):
    for n,color in enumerate(wheel.colors):
        row = layout.row(align=True)
        row.prop(color,'color',text='')
        row.operator('gradience.del',icon='X',text='',emboss=False).n = n

def gradience_tools(layout,wheel):
    row = layout.row()

class GRADIENCE_PT_gradience(bpy.types.Panel):
    bl_label = "Chromatone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    def draw_header(self,context):
        self.layout.operator("gradience.add",text=str(len(context.active_object.gradience.colors)),icon="ZOOMIN")
    def draw(self,context):
        layout = self.layout
        wheel = context.active_object.gradience
        gradience_controls(layout,wheel)
        gradience_display(layout,wheel)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Object.gradience = bpy.props.PointerProperty(type=ChromatonicProp)

def unregister():
    del bpy.types.Object.gradience
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()



