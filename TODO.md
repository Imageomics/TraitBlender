
##IN PROGRESS

### Task 6
Sometimes textures aren't exported or look funny when viewed in other 3D viewports.

### Task 9
Make a Docker image.

### Maybe make background panels an dataset option?




##COMPLETE
### Task 1
Fix the erroneous button in the "Select Mesh Function" part of the menu.

### Task 2
Fix the weird warning when importing the mesh function CSV.

### Task 3
Maybe add the ability to hide individual background planes? //I don't think it really matters

### Task 5
Sometimes the object does not show up in the final render even though it is apparent in the camera view. 
This seems to mostly happen when the background planes are present; they may be in the way for the render but not the camera. 
	- Solved, this happens when the distance from the background of the object from one side is different from
	  another side, like when you have a flat square. This makes the background mush closer to one side of the object 
          then another side, which makes it easy to accidently hide the object. We can either fix this by having the distance 
	  get added to the joint distance from both sides, or just telling people to be careful.

### Task 7
Need docstrings and other function/operator documentation.

### Task 4
After you hide an individual sun, you can no longer use the "hide all suns" button properly; it will only hide/unhide the last hidden sun. Fix this.

### Task 11
Fix it so that backgrounds can be scaled on single axes, they currently only scale on all 3 at once
## --> This seems to be a non-issue, it might have been the way I loaded the addon messing up the one time


### Task 10
Publish to Blender addons catalogue.
- Publishing instructions can be found [here](https://wiki.blender.org/wiki/Process/Addons/Guidelines "Publishing Requirements").


### Task 8
Need to clean up the generating loop with the new operators.

### Task 12
Fix the export function for the generating loop to export all the parameters correctly