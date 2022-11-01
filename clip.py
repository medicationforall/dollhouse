import cadquery as cq

def clip():
    #log('make clip')
    part1 = cq.Workplane("XY").box(12.5, 24, 8)
    inner = cq.Workplane("XY").box(8.5,22,8).translate((0,-1,0))
    combined = part1.cut(inner)
    combined = combined.fillet(.3)
    return combined

part_clip = clip()
#show_object(part_clip)
cq.exporters.export(part_clip,'out/clip_long.stl')