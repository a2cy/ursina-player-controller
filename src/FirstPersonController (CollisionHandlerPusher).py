from ursina import *

from panda3d.core import CollisionTraverser, CollisionHandlerPusher


class FirstPersonController(Entity):
    
    def __init__(self, **kwargs):
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)
        super().__init__()
        self.speed = 6
        self.acceleration = 12
        self.height = 2

        self.camera_pivot = Entity(parent=self, y=self.height)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0,0,0)
        camera.rotation = Vec3(0,0,0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(60,60)

        self.gravity = 1
        self.jumping = False
        self.grounded = False
        self.jump_height = 2
        self.jump_up_duration = .5
        self.fall_after = .35 # will interrupt jump up
        self.air_time = 0
        self.direction = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)

        self.traverse_target = scene     # by default, it will collide with everything. change this to change the raycasts' traverse targets.
        self.ignore_list = [self, ]
        self.collider="capsule"

        self.trav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        node = self.collider.node_path

        self.trav.addCollider(node, self.pusher)
        self.pusher.addCollider(node, self)

        for key, value in kwargs.items():
            setattr(self, key ,value)

        # make sure we don't fall through the ground if we start inside it
        if self.gravity:
            ray = raycast(self.world_position+(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)
            if ray.hit:
                self.y = ray.world_point.y


    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])
            ).normalized()
        
        self.velocity = lerp(self.velocity, self.direction * self.speed, self.acceleration * time.dt)

        self.position += self.velocity * time.dt

        self.trav.traverse(self.traverse_target)

        # gravity
        if self.gravity:
            ray = raycast(self.world_position+Vec3(0,self.height,0), self.down, traverse_target=self.traverse_target, ignore=self.ignore_list)

            if ray.distance <= self.height+.1:
                self.air_time = 0
                self.grounded = True
                # make sure it's not a wall and that the point is not too far up
                if ray.world_normal.y > .7 and ray.world_point.y - self.world_y < .5: # walk up slope
                    self.y = ray.world_point[1]
            else:
                self.grounded = False

                # if not on ground and not on way up in jump, fall
                self.y -= min(self.air_time, ray.distance-.05) * time.dt * 100
                self.air_time += time.dt * .25 * self.gravity


    def input(self, key):
        if key == 'space':
            self.jump()


    def jump(self):
        if not self.grounded:
            return
        
        self.jumping = True
        self.grounded = False

        ray = raycast(self.world_position+Vec3(0,self.height-.1,0), self.up, ignore=(self,), distance=.2+self.jump_height)
        self.animate_y(self.y+min(self.jump_height, ray.distance-.2), self.jump_up_duration, resolution=int(1//time.dt), curve=curve.out_expo)
        invoke(self.start_fall, delay=self.fall_after)

    
    def start_fall(self):
        self.jumping = False
        self.y_animator.pause()


    def on_enable(self):
        mouse.locked = True
        self.cursor.enabled = True


    def on_disable(self):
        mouse.locked = False
        self.cursor.enabled = False


if __name__ == "__main__":
    # from ursina.prefabs.first_person_controller import FirstPersonController
    app = Ursina(borderless = False)

    ground = Entity(model="plane", texture="grass", collider="box", scale=Vec3(1000, 1, 1000), texture_scale=Vec2(1000, 1000))

    wall1 = Entity(model="cube", texture="brick", collider="box", scale=Vec3(1, 3, 5), position=Vec3(2, 1.5, 0), texture_scale=Vec2(5, 3))

    wall2 = Entity(model="cube", texture="brick", collider="box", scale=Vec3(16, 3, 1), position=Vec3(-5, 1.5, 5), rotation=Vec3(0, 30, 0), texture_scale=Vec2(15, 3))

    ceiling = Entity(model="cube", texture="brick", collider="box", scale=Vec3(3, 1, 5), position=Vec3(3, 3.5, 0), texture_scale=Vec2(5, 3))

    slope = Entity(model="cube", texture="brick", collider="box", scale=Vec3(5, 3, 3), position=Vec3(-5, 1, 0), rotation=Vec3(0, 0, 10), texture_scale=Vec2(5, 3))

    player = FirstPersonController(y=.5)

    def input(key):
        if key == "escape":
            mouse.locked = not mouse.locked

    app.run()