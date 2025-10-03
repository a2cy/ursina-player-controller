from ursina import *
from FirstPersonController import AABBCollider


app = Ursina()

static_box = Entity(parent=camera.ui, model="quad", scale=0.1)
moving_box_a = Entity(parent=camera.ui, model="quad", scale=0.1, color=color.orange, z=-0.01)
moving_box_b = Entity(parent=camera.ui, model="quad", scale=0.1, color=color.azure, z=-0.01)

line_a_to_b = Entity(parent=camera.ui, model=Mesh(mode="line", thickness=4), color=color.light_gray)
box_after_collision = Entity(parent=camera.ui, model="quad", scale=0.1, color=color.green, enabled=False)

static_collider = AABBCollider(Vec3(0), Vec3(0), Vec3(0.1))
moving_collider = AABBCollider(Vec3(0), Vec3(0), Vec3(0.1))

screen_collider = Entity(parent=camera.ui, model="cube", collider="box", scale=2, visible=False)


def update():
    if mouse.position:
        moving_box_b.position = Vec3(mouse.x, mouse.y, -0.01)
        line_a_to_b.model.vertices = [Vec3(moving_box_a.position.xy, 0.0), Vec3(moving_box_b.position.xy, 0.0)]
        line_a_to_b.model.generate()

    move_delta = moving_box_b.position - moving_box_a.position
    collision_time, normal = moving_collider.collide(static_collider, move_delta)
    box_after_collision.enabled = False

    if normal:
        box_after_collision.position = moving_box_a.position + move_delta * collision_time
        box_after_collision.enabled = True


def input(key):
    if key == "left mouse down" and mouse.position:
        moving_box_a.position = Vec3(mouse.x, mouse.y, -0.01)
        moving_collider.position = Vec3(mouse.x, mouse.y, 0.0)


app.run()
