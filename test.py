import cadquery as cq
from cqterrain import Building



cq_editor_show = False
export_to_file = True


result = cq.importers.importStep('stl/floral.step')

if cq_editor_show:
    #show_object(scene)
    show_obbject(result)

