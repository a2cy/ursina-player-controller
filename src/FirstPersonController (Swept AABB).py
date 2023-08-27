from ursina import *


class AABB:
    def __init__(self, position: Vec3, shape: list):
        self.position = position
        self.shape = shape


    @property
    def x(self):
        return self.position.x

    @property
    def y(self):
        return self.position.y

    @property
    def z(self):
        return self.position.z

    @property
    def x_1(self):
        return self.shape[0] + self.position.x

    @property
    def y_1(self):
        return self.shape[1] + self.position.y

    @property
    def z_1(self):
        return self.shape[2] + self.position.z

    @property
    def x_2(self):
        return self.shape[3] + self.position.x
    
    @property
    def y_2(self):
        return self.shape[4] + self.position.y
    
    @property
    def z_2(self):
        return self.shape[5] + self.position.z


class Player(Entity):

    def __init__(self, colliders, **kwargs):
        super().__init__()
        self.speed = 6
        self.acceleration = 16
        self.gravity = 3.4
        self.jump_height = 1.4

        self.noclip_speed = 8
        self.noclip_acceleration = 6

        self.colliders = colliders
        self.aabb_collider = AABB(self.position, [-.5, -1.5, -.5,  .5, .4, .5])

        self.noclip_mode = False

        self.camera_pivot = Entity(parent=self)
        camera.parent = self.camera_pivot
        camera.position = Vec3(0,0,0)
        camera.rotation = Vec3(0,0,0)
        camera.fov = 90
        self.mouse_sensitivity = 80

        self.grounded = False
        self.airtime = 0
        self.direction = Vec3(0,0,0)
        self.velocity = Vec3(0,0,0)

        for key, value in kwargs.items():
            setattr(self, key, value)

    
    def aabb_broadphase(self, collider_1, collider_2, direction):
        x_1 = min(collider_1.x_1, collider_1.x_1 + direction.x)
        y_1 = min(collider_1.y_1, collider_1.y_1 + direction.y)
        z_1 = min(collider_1.z_1, collider_1.z_1 + direction.z)

        x_2 = max(collider_1.x_2, collider_1.x_2 + direction.x)
        y_2 = max(collider_1.y_2, collider_1.y_2 + direction.y)
        z_2 = max(collider_1.z_2, collider_1.z_2 + direction.z)

        return not (x_2 < collider_2.x_1 or
                    x_1 > collider_2.x_2 or
                    y_2 < collider_2.y_1 or
                    y_1 > collider_2.y_2 or
                    z_2 < collider_2.z_1 or
                    z_1 > collider_2.z_2)


    def swept_aabb(self, collider_1, collider_2, direction):
        x_inv_entry = collider_2.x_1 - collider_1.x_2 if direction.x > 0 else collider_2.x_2 - collider_1.x_1
        x_inv_exit = collider_2.x_2 - collider_1.x_1 if direction.x > 0 else collider_2.x_1 - collider_1.x_2

        y_inv_entry = collider_2.y_1 - collider_1.y_2 if direction.y > 0 else collider_2.y_2 - collider_1.y_1
        y_inv_exit = collider_2.y_2 - collider_1.y_1 if direction.y > 0 else collider_2.y_1 - collider_1.y_2

        z_inv_entry = collider_2.z_1 - collider_1.z_2 if direction.z > 0 else collider_2.z_2 - collider_1.z_1
        z_inv_exit = collider_2.z_2 - collider_1.z_1 if direction.z > 0 else collider_2.z_1 - collider_1.z_2

        x_entry = -inf if direction.x == 0 else x_inv_entry / direction.x
        x_exit = inf if direction.x == 0 else x_inv_exit / direction.x

        y_entry = -inf if direction.y == 0 else y_inv_entry / direction.y
        y_exit = inf if direction.y == 0 else y_inv_exit / direction.y

        z_entry = -inf if direction.z == 0 else z_inv_entry / direction.z
        z_exit = inf if direction.z == 0 else z_inv_exit / direction.z

        entry_time = max([x_entry, y_entry, z_entry])
        exit_time = min([x_exit, y_exit, z_exit])

        if entry_time > exit_time or x_entry < 0 and y_entry < 0 and z_entry < 0 or x_entry > 1 or y_entry > 1 or z_entry > 1:
            return 1, Vec3(0, 0, 0)

        normal_x = (0, -1 if direction.x > 0 else 1)[entry_time == x_entry]
        normal_y = (0, -1 if direction.y > 0 else 1)[entry_time == y_entry]
        normal_z = (0, -1 if direction.z > 0 else 1)[entry_time == z_entry]

        return entry_time, Vec3(normal_x, normal_y, normal_z)


    def update(self):
        if self.noclip_mode:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

            self.direction = Vec3(self.camera_pivot.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()

            self.direction += self.up * (held_keys["e"] - held_keys["q"])

            self.velocity = lerp(self.velocity, self.direction * self.noclip_speed * time.dt, self.noclip_acceleration * time.dt)

            self.position += self.velocity
        
        else:
            self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity

            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

            self.direction = Vec3(self.forward * (held_keys["w"] - held_keys["s"])
                                  + self.right * (held_keys["d"] - held_keys["a"])).normalized()
            
            self.airtime += time.dt

            self.direction.y -= self.gravity * self.airtime

            self.velocity = lerp(self.velocity, self.direction * self.speed * time.dt, self.acceleration * time.dt)

            self.aabb_collider.position = self.position

            for _ in range(3):
                collisions = []

                for collider in self.colliders:
                    if self.aabb_broadphase(self.aabb_collider, collider, self.velocity):
                        collision_time, collision_normal = self.swept_aabb(self.aabb_collider, collider, self.velocity)

                        collisions.append((collision_time, collision_normal))

                if not collisions:
                    break

                collision_time, collision_normal = min(collisions, key= lambda x: x[0])

                remaining_time = 1 - collision_time

                response = self.velocity - self.velocity.project(collision_normal)
                response = Vec3.zero if response.is_nan() else response * remaining_time

                self.velocity = self.velocity * collision_time + response

            if self.velocity.y == 0:
                self.grounded = True
                self.airtime = 0

            else:
                self.grounded = False

            self.position += self.velocity


    def input(self, key):
        if key == "space":
            if self.grounded and not self.noclip_mode:
                self.velocity.y += self.jump_height / self.gravity


    def on_enable(self):
        mouse.locked = True


    def on_disable(self):
        mouse.locked = False


if __name__ == "__main__":
    app = Ursina(borderless=False)

    colliders = []

    box_1 = Entity(model="cube", texture="brick", position=Vec3(4, 3, 0), scale=Vec3(2, 1, 3), texture_scale=Vec2(2, 3))
    box_2 = Entity(model="cube", texture="brick", position=Vec3(3, 1.5, 0), scale=Vec3(1, 2, 3), texture_scale=Vec2(2, 3))
    box_3 = Entity(model="cube", texture="grass", position=Vec3(0, 0, 0), scale=Vec3(25, 1, 25), texture_scale=Vec2(25, 25))
    box_4 = Entity(model="cube", texture="brick", position=Vec3(-2, 1.5, 0), scale=Vec3(2, 2, 2), texture_scale=Vec2(2, 2))

    collider_1 = AABB(box_1.position, [-1, -.5, -1.5,  1, .5, 1.5])
    collider_2 = AABB(box_2.position, [-.5, -1, -1.5,  .5, 1, 1.5])
    collider_3 = AABB(box_3.position, [-12.5, -.5, -12.5,  12.5, .5, 12.5])
    collider_4 = AABB(box_4.position, [-1, -1, -1,  1, 1, 1])

    colliders.extend([collider_1, collider_2, collider_3, collider_4])

    player = Player(colliders, position=Vec3(0, 5, 0))

    def input(key):
        if key == "escape":
            mouse.locked = not mouse.locked

        if key == "k":
            player.noclip_mode = not player.noclip_mode

    app.run()
