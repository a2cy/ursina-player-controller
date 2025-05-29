# FirstPersonController

Player controller template made for ursina engine 7.  
Uses a sweep test against axis aligned bounding boxes.  

## AABBCollider

A collider takes 3 arguments `position`, `origin` and `scale` which all have to be Vec3's. The position can be changed after creation however origin and scale cannot.  

There are two methods for collision detection being `intersect` and `collide`. 

`intersect` takes another collider and returns a bool whether they intersect or not.  

`collide` takes another collider to collide into and a move_delta which is the amount you want the collider to move and returns a tuple containing a value from 0 to 1 that multiplied by move_delta results in the distance to the "into" collider if a collision occured and the normal vector of the surface it collided into.

## Player

Needs a list of colliders to collide against.  
Also has a noclip mode which can be enabled by setting `noclip_mode` to True.  