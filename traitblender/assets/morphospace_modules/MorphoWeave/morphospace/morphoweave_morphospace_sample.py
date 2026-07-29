"""Blender mesh creation for a MorphoWeave warped template."""

import bpy


class MorphoWeaveMorphospaceSample:
    def __init__(self, name: str, vertices: list, faces: list):
        self.name = name
        self.vertices = vertices
        self.faces = faces

    def to_blender(self) -> None:
        mesh = bpy.data.meshes.new(name=f"{self.name}_mesh")
        mesh.from_pydata(self.vertices, [], self.faces)
        mesh.update()

        obj = bpy.data.objects.new(self.name, mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
