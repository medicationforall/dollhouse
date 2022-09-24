import cadquery as cq
from cqterrain import Building

def make_arch_door(wall, length, width, height):
    window_cutout = cq.Workplane().box(length, width, height)
    w = wall.cut(window_cutout)
    return w

def make_kitchen():
    log('make_left')
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, True, False]
    bp.room['door_walls'] = [False, False, False, True]
    bp.room['make_custom_door'] = make_arch_door

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
    log('make_center')
    bp = Building(length=125, width=175, height=350, stories=2)
    bp.room['build_walls']= [False,True,False,False]
    bp.room['window_walls'] = [False, False, False, False]
    bp.make()
    bp.floors[0].door_walls = [False, True, False, False]
    bp.floors[0].make()
    center = bp.build()
    return center

def make_living():
    log('make_right')
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, False, True]
    bp.room['door_walls'] = [False, False, True, False]
    bp.room['make_custom_door'] = make_arch_door

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
show_object(scene)
