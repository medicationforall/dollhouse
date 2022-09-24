import cadquery as cq
from cqterrain import Building

cq_editor_show = False
export_to_file = True

def make_arch_door(wall, length, width, height, floor_height):
    bottom = wall.faces("-Z").val()
    cutout = (cq.Workplane(bottom.Center())
              .box(length, width, height)
              .translate((0,0,(height/2)+floor_height))
              )
    cutout = cutout.faces("Z").edges("Y").fillet((length/2)-.5)

    log(bottom.Center())
    w = wall.cut(cutout)
    return w

def make_kitchen():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, True, False]
    bp.room['door_walls'] = [False, False, False, True]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 45
    bp.window['length'] = 58


    bp.make()
    bp.floors[0].window_count=3
    bp.floors[0].window['height'] = 45
    bp.floors[0].window['length'] = 28

    bp.floors[0].make()
    left = bp.build()
    return left

def make_center():
    bp = Building(length=125, width=175, height=350, stories=2)
    bp.room['build_walls']= [False,True,False,False]
    bp.room['window_walls'] = [False, False, False, False]

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.make()
    bp.floors[0].door_walls = [False, True, False, False]
    bp.floors[0].make()
    center = bp.build()
    return center

def make_living():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, False, True]
    bp.room['door_walls'] = [False, False, True, False]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 45
    bp.window['length'] = 58

    bp.make()
    right = bp.build()
    return right


left = make_kitchen().translate((87.5 + 62.5,0,0))
center = make_center()
right = make_living().translate((-87.5 - 62.5,0,0))

scene = (cq.Workplane("XY")
         .add(left)
         .add(center)
         .add(right)
         )

if cq_editor_show:
    show_object(scene)

if export_to_file:
    cq.exporters.export(scene,'out/dollhouse.stl')
