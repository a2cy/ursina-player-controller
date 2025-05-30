from ursina import *
from FirstPersonController import AABBCollider


app = Ursina()

static_box = Entity(parent=camera.ui, model="quad", scale=0.1)
moving_box_b = Entity(parent=camera.ui, model="quad", scale=0.1, color=color.azure, z=-0.01)

static_collider = AABBCollider(Vec3(0), Vec3(0), Vec3(0.1))
moving_collider = AABBCollider(Vec3(0), Vec3(0), Vec3(0.1))

screen_collider = Entity(parent=camera.ui, model="cube", collider="box", scale=2, visible=False)


def update():
    if mouse.position:
        moving_box_b.position = Vec3(mouse.x, mouse.y, -0.01)
        moving_collider.position = Vec3(mouse.x, mouse.y, 0.0)

    if moving_collider.intersect(static_collider):
        moving_box_b.color = color.red
    else:
        moving_box_b.color = color.azure


app.run()