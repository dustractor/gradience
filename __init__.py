bl_info = {
    "name": "Gradience",
    "author": "dustractor@gmail.com",
    "version": (0, 1),
    "blender": (2, 7, 2),
    "location": "3d View -> Tools",
    "description": "frequency/amplitude/offset modulation (sine) of hue/saturation/value creating a sequence of varying length (size parameter) which is applied to targets (currently only blender internal materials' diffuse_color value)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/dustractor/gradience",
    "category": "Material"}

# imports {{{1
import random
import itertools
import math
import bpy

# functions {{{1

# choosename {{{2

def choosename(name,names):
    nameslike = sorted([n for n in names if n.startswith(name)])
    if nameslike:
        lastn = nameslike[-1]
        lastsufx = 0
        if lastn.count("."):
            try:
                lastsufx = int(lastn.rpartition(".")[2])
            except ValueError:
                pass
        return "%s.%03d" % (name,lastsufx + 1)
    return name

# compute_gradience {{{2

def compute_gradience(g,c):
    step = 1.0 / g.size
    hue,sat,val = g.base
    hf,hm,ho = g.hvec
    sf,sm,so = g.svec
    vf,vm,vo = g.vvec
    for n in range(g.size):
        i = g.offset + ( step * n )
        hue += math.sin((i * hf ) + ho ) * hm
        sat += math.sin((i * sf ) + so ) * sm
        val += math.sin((i * vf ) + vo ) * vm
        t = (math.modf(hue)[0],math.modf(sat)[0],math.modf(val)[0])
        g.stops[n].color.hsv = t

# size_update {{{2

def size_update(g,c):
    g.stops.clear()
    list(map(lambda _:g.stops.add(),range(g.size)))
    compute_gradience(g,c)

# targets {{{2


def targets(context):
    print("context:",context)
    for ob in context.selected_objects:
        if ob.type == "MESH":
            for mat in (_.material for _ in ob.material_slots):
                yield mat,"diffuse_color"


# PropertyGroup classes {{{1
# GradienceColorStop {{{2


class GradienceColorStop(bpy.types.PropertyGroup):
    color = bpy.props.FloatVectorProperty(subtype="COLOR",min=0.0,max=1.0)


# GradienceTarget {{{2


class GradienceTarget(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()


# GradienceTargeting {{{2


class GradienceTargeting(bpy.types.PropertyGroup):
    method = bpy.props.EnumProperty(
            items=[(_,_,_) for _ in ("Selection","Custom")])
    targets = bpy.props.CollectionProperty(type=GradienceTarget)
    targets_i = bpy.props.IntProperty(default=-1,min=-1)


# GradienceItem {{{2


class GradienceItem(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    targeting = bpy.props.PointerProperty(type=GradienceTargeting)
    offset = bpy.props.FloatProperty(update=compute_gradience)
    base = bpy.props.FloatVectorProperty(
            precision=5,size=3,min=0.0,max=1.0,update=compute_gradience)
    hvec = bpy.props.FloatVectorProperty(
            precision=5,size=3,min=0.0,max=1.0,update=compute_gradience)
    svec = bpy.props.FloatVectorProperty(
            precision=5,size=3,min=0.0,max=1.0,update=compute_gradience)
    vvec = bpy.props.FloatVectorProperty(
            precision=5,size=3,min=0.0,max=1.0,update=compute_gradience)
    g_mtx = bpy.props.FloatVectorProperty(
            size=9,soft_min=-1.0,soft_max=1.0,update=compute_gradience)
    size = bpy.props.IntProperty(
            min=1,soft_max=256,default=1,update=size_update)
    stops = bpy.props.CollectionProperty(type=GradienceColorStop)
    cols = bpy.props.IntProperty(default=1,min=1,max=32)


# Gradience {{{2


class Gradience(bpy.types.PropertyGroup):
    data = bpy.props.CollectionProperty(type=GradienceItem)
    data_i = bpy.props.IntProperty(default=-1,min=-1)
    active = property(fget=lambda s:s.data[s.data_i] if s.data_i > -1 else None)


# Operator classes {{{1
# GRADIENCE_OT_randomize_gradience_item {{{2


class GRADIENCE_OT_randomize_gradience_item(bpy.types.Operator):
    bl_idname = "gradience.randomize_gradience_item"
    bl_label = "gradience:Randomize Gradience Item"
    item = bpy.props.IntProperty(default=-1)
    affect = bpy.props.StringProperty(default="hsv")

    def execute(self,context):
        G = context.scene.gradience
        if self.item == -1:
            g = G.active
        else:
            g = G.data[self.item]
        if "h" in self.affect:
            g.hvec = [random.random() for _ in range(3)]
        if "s" in self.affect:
            g.svec = [random.random() for _ in range(3)]
        if "v" in self.affect:
            g.vvec = [random.random() for _ in range(3)]
        if "b" in self.affect:
            g.base = [random.random() for _ in range(3)]
        if "o" in self.affect:
            g.offset = random.random()
        return {"FINISHED"}


# GRADIENCE_OT_add_gradience_item {{{2


class GRADIENCE_OT_add_gradience_item(bpy.types.Operator):
    bl_idname = "gradience.add_gradience_item"
    bl_label = "gradience:Add Gradience Item"

    def execute(self,context):
        G = context.scene.gradience
        names = [d.name for d in G.data]
        n = G.data.add()
        name = "Set"
        n.name = choosename(name,names)
        n.size = 7
        G.data_i = len(G.data) - 1
        return {"FINISHED"}


# GRADIENCE_OT_remove_gradience_item {{{2


class GRADIENCE_OT_remove_gradience_item(bpy.types.Operator):
    bl_idname = "gradience.remove_gradience_item"
    bl_label = "gradience:Remove Gradience Item"

    def execute(self,context):
        G = context.scene.gradience
        G.data.remove(G.data_i)
        G.data_i = len(G.data) - 1
        return {"FINISHED"}


# GRADIENCE_OT_gradience_select {{{2


class GRADIENCE_OT_gradience_select(bpy.types.Operator):
    bl_idname = "gradience.select_gradience"
    bl_label = "gradience:Select Gradience Item"
    data_i = bpy.props.IntProperty()

    def execute(self,context):
        G = context.scene.gradience
        G.data_i = self.data_i
        return {"FINISHED"}


# GRADIENCE_OT_gradience_apply {{{2


class GRADIENCE_OT_gradience_apply(bpy.types.Operator):
    bl_idname = "gradience.apply_gradience"
    bl_label = "gradience:Apply Gradience to Target(s)"

    def execute(self,context):
        G = context.scene.gradience
        active = G.active
        stop = itertools.cycle([_.color for _ in active.stops])
        list(map(lambda t:setattr(t[0],t[1],next(stop)),targets(context)))
        return {"FINISHED"}


# GRADIENCE_OT_add_gradience_targets {{{2


class GRADIENCE_OT_add_gradience_targets(bpy.types.Operator):
    bl_idname = "gradience.add_gradience_targets"
    bl_label = "gradience:Add Gradience Targets"

    def execute(self,context):
        G = context.scene.gradience
        active = G.active
        targeting = active.targeting
        print("targeting:",targeting)
        return {"FINISHED"}


# Interface classes {{{1
# GRADIENCE_UL_gradience_targets {{{2


class GRADIENCE_UL_gradience_targets(bpy.types.UIList):

    def draw_item(self,context,layout,data,item,icon,ac_data,ac_propname):
        row = layout.row(align=True)
        row.label(icon="SETTINGS",text=item.name)


# GRADIENCE_MT_gradience_menu {{{2


class GRADIENCE_MT_gradience_menu(bpy.types.Menu):
    bl_label = "Gradience"

    def draw(self,context):
        layout = self.layout
        G = context.scene.gradience
        layout.operator("gradience.add_gradience_item",text="Add Gradience")
        if G.data_i < 0:
            return
        layout.operator("gradience.remove_gradience_item",text="Remove Gradience")
        layout.separator()
        for n in range(len(G.data)):
            g = G.data[n]
            icon = ["BLANK1","FILE_TICK"][n==G.data_i]
            mi = layout.operator(
                    "gradience.select_gradience",
                    text="Select Gradience: " + g.name,icon=icon)
            mi.data_i = n
        layout.separator()
        layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience HSV")
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience H")
        op.affect = "h"
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience S")
        op.affect = "s"
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience V")
        op.affect = "v"
        layout.separator()
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience HSV+Base")
        op.affect = "hsvb"
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience HSV+Base+Offset")
        op.affect = "hsvbo"
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience Base")
        op.affect = "b"
        op = layout.operator(
                "gradience.randomize_gradience_item",
                text="Randomize Gradience Offset")
        op.affect = "o"
        layout.separator()
        layout.label(text="(Utility)")
        layout.operator("object.make_single_user",
                text="Make Single User (Materials)").material = True
        layout.separator()
        layout.operator("gradience.add_gradience_targets",
                text="Add Custom Targets...")
        layout.operator("gradience.apply_gradience",
                text="Apply Gradience to Targets")


# GRADIENCE_PT_gradience_panel {{{2


class GRADIENCE_PT_gradience_panel(bpy.types.Panel):
    bl_category = "Gradience"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Settings"
    bl_options = {"HIDE_HEADER"}

    def draw(self,context):
        layout = self.layout
        G = context.scene.gradience
        active = G.active
        targeting = active.targeting if active else None
        row = self.layout.row(align=True)
        row.menu("GRADIENCE_MT_gradience_menu",text="",icon="SETTINGS")
        label = active.name if active else ""
        row.label(text=label)
        col = layout.column(align=True)
        if active:
            col.prop(active,"size",text="Size")
            col.prop(active,"offset",text="Offset")
            col.prop(active,"base",slider=True)
            col.prop(active,"hvec",slider=True)
            col.prop(active,"svec",slider=True)
            col.prop(active,"vvec",slider=True)
            col.separator()
            col.operator("gradience.randomize_gradience_item",
                    text="Random HSV")
            col.separator()
            col.operator("object.make_single_user",
                text="Make Single User (Materials)").material = True
            col.operator("gradience.apply_gradience",
                text="Apply")
            col.separator()
            layout.box().prop(active,"cols")
            col = layout.column(align=True)
            cell = col
            for n in range(active.size):
                if not (n % active.cols):
                    cell = col.row(align=True)
                cell.prop(active.stops[n],"color",text="")
            layout.separator()
            layout.prop_enum(targeting,"method","Selection")
            layout.prop_enum(targeting,"method","Custom")
            if targeting.method == "Custom":
                layout.template_list(
                        "GRADIENCE_UL_gradience_targets","",
                        targeting,"targets",targeting,"targets_i")
                layout.operator(
                        "gradience.add_gradience_targets",
                        text="Add Targets...",icon="ZOOMIN")


# registration {{{1

# functions {{{2

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.gradience = bpy.props.PointerProperty(type=Gradience)

def unregister():
    del bpy.types.Scene.gradience
    bpy.utils.unregister_module(__name__)
