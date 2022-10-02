import cadquery as cq
from cqterrain import Building, window, roof
from cadqueryhelper import series

cq_editor_show = False
export_to_file = True
render_floor = False
render_roof_tiles = True

def make_roof(roof_width=185):
    gable_roof_raw = roof.dollhouse_gable(length=roof_width, width=185, height=100)
    gable_roof = roof.shell(gable_roof_raw,face="Y", width=-4)
    angle = roof.angle(185, 100)
    face_x = gable_roof_raw.faces("<X")

    if render_roof_tiles:
        tile = cq.Workplane("XY").box(8,8,2).rotate((0,1,0),(0,0,0),8)
        tiles = roof.tiles(tile, face_x, 185, 100, 8, 8, angle, rows=28, odd_col_push=[1,0], intersect=False).rotate((0,0,1),(0,0,0),90).translate((3,45,0))
        inter_tiles = cq.Workplane("XY").box(roof_width,185, 100)
        inter_tiles = tiles.intersect(inter_tiles)

        return gable_roof.add(inter_tiles)
    else:
        return gable_roof


def lattice_windows(wall, length, width, height, count, padding):
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    lattice = window.lattice(length=length, width=4, height=height, tile_size=6, lattice_height=2)
    i_window.add(lattice)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

def casement_windows(wall, length, width, height, count, padding):
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    grill = window.grill(length=length, width=4, height=height, rows=4, columns=2, grill_width=2, grill_height=3)
    i_window.add(grill)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

def casement_windows_2(wall, length, width, height, count, padding):
    window_cutout = cq.Workplane().box(length, width, height)
    window_cut_series = series(window_cutout, count, length_offset = padding)

    i_window = window.frame(length, width+3, height)
    grill = window.grill(length=length, width=4, height=height, rows=4, columns=4, grill_width=2, grill_height=3)
    i_window.add(grill)
    window_series = series(i_window, count, length_offset = padding)

    w = wall.cut(window_cut_series)
    w = w.add(window_series)

    return w

if render_floor:
    pattern = cq.importers.importStep('stl/floral.step')
    scaled = pattern.val().scale(0.15)
    center = scaled.CenterOfBoundBox()
    pattern = cq.Workplane().add(scaled).translate((center.x*-1,center.y*-1,center.z*-1))


def make_arch_door(wall, length, width, height, floor_height):
    bottom = wall.faces("-Z").val()
    cutout = (cq.Workplane(bottom.Center())
              .box(length, width, height)
              .translate((0,0,(height/2)+floor_height))
              )
    cutout = cutout.faces("Z").edges("Y").fillet((length/2)-.5)
    w = wall.cut(cutout)
    return w

def make_kitchen():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, True, False]
    bp.room['door_walls'] = [False, False, False, True]
    bp.room['make_custom_door'] = make_arch_door
    if render_floor:
        bp.room['floor_tile'] = pattern
        bp.room['floor_tile_padding'] = .5

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 55
    bp.window['length'] = 78

    bp.make()
    bp.floors[0].window_count=4
    bp.floors[0].window['height'] = 45
    bp.floors[0].window['length'] = 28
    bp.floors[0].make_custom_windows = casement_windows
    bp.floors[0].make()

    bp.floors[1].make_custom_windows = lattice_windows
    bp.floors[1].make()

    left = bp.build()
    left_roof = make_roof().translate((5,-5,312.5))
    combine = cq.Workplane("XY").add(left).add(left_roof)
    return combine

def make_center():
    bp = Building(length=125, width=175, height=350, stories=2)
    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, False, False, False]
    bp.room['door_walls'] = [False, False, True, True]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.make()
    bp.floors[0].door_walls = [False, True, True, True]
    bp.floors[0].make()
    center = bp.build()

    center_roof = make_roof(125).translate((0,-5,312.5))
    combine = cq.Workplane("XY").add(center).add(center_roof)
    return combine

    return center

def make_living():
    bp = Building(length=175, width=175, height=350, stories=2)

    bp.room['build_walls']= [False,True,True,True]
    bp.room['window_walls'] = [False, True, False, True]
    bp.room['door_walls'] = [False, False, True, False]
    bp.room['make_custom_door'] = make_arch_door

    bp.door['length'] = 60
    bp.door['height'] = 100

    bp.window['height'] = 55
    bp.window['length'] = 78

    bp.make()

    bp.floors[0].make_custom_windows = casement_windows_2
    bp.floors[0].make()

    bp.floors[1].make_custom_windows = lattice_windows
    bp.floors[1].make()

    right = bp.build()
    right_roof = make_roof().translate((-5,-5,312.5))
    combine = cq.Workplane("XY").add(right).add(right_roof)
    return combine


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
