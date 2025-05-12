# FirstPersonController

Player controller template made for ursina engine 7.  
It uses a sweep test against axis aligned bounding boxes.  

## The collider

A collider takes 3 arguments `position`, `origin` and `scale` which all have to be Vec3's. The position can be changed after creation however origin and scale cannot.  

There are two methods for collision detection outside of the Player class being `intersect` and `collide`. 

`intersect` takes another collider and returns a bool whether they intersect or not.  

`collide` takes another collider to collide into and a move_delta which is the amount you want the collider to move and returns a tuple containing a value from 0 to 1 that multiplied by move_delta results in the distance to the "into" collider if a collision occured and the normal vector of the surface it collided into.

## The player

The Player can take the same arguments an `Entity` can.  
Additionally it needs a list of colliders to collide against.  

It also has a noclip mode which can be enabled by setting `noclip_mode` to True.

## Example

A runnable example can be found in the implementation file.

```python
ground_collider = AABBCollider(Vec3(0, 0, 0), Vec3(0, 0, 0), Vec3(10, 1, 10))

wall_collider = AABBCollider(Vec3(2, 0, 0), Vec3(0, 0, 0), Vec3(1, 5, 10))

collider_list = [ground_collider, wall_collider]

player = Player(collider_list, position=Vec3(0, 2, 0))
```
