# Copyright 2022 James Adams
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
