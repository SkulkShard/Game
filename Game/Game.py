import pygame
import sys

class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2
        self.ground_surf = pygame.image.load('Images/Map/Ground.png').convert_alpha()
        self.ground_rect = self.ground_surf.get_rect(center=(self.half_w, self.half_h))
        self.keyboard_speed = 5
        self.zoom_scale = 1.0
        self.internal_surf_size = (2500, 2500)
        self.internal_surf = pygame.Surface(self.internal_surf_size, pygame.SRCALPHA)
        self.internal_rect = self.internal_surf.get_rect(center=(self.half_w, self.half_h))
        self.internal_surface_size_vector = pygame.math.Vector2(self.internal_surf_size)
        self.internal_offset = pygame.math.Vector2()
        self.internal_offset.x = self.internal_surf_size[0] // 2 - self.half_w
        self.internal_offset.y = self.internal_surf_size[1] // 2 - self.half_h
        self.min_zoom = 0.5
        self.max_zoom = 5
        self.zoom_speed = 0.1
        self.target_zoom = self.zoom_scale
        self.center_camera_on_map()

    def center_camera_on_map(self):
        self.offset.x = self.ground_rect.width // 2 - self.half_w
        self.offset.y = self.ground_rect.height // 2 - self.half_h

    def keyboard_control(self):
        keys = pygame.key.get_pressed()
        move_speed = self.keyboard_speed / self.zoom_scale
        if keys[pygame.K_a]: self.offset.x -= move_speed
        if keys[pygame.K_d]: self.offset.x += move_speed
        if keys[pygame.K_w]: self.offset.y -= move_speed
        if keys[pygame.K_s]: self.offset.y += move_speed

        # Constrain the camera's offset to ensure it doesn't move outside the map
        self.constrain_camera()

    def zoom_keyboard_control(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_q]:
            self.target_zoom = min(self.target_zoom + self.zoom_speed, self.max_zoom)
        if keys[pygame.K_e]:
            self.target_zoom = max(self.target_zoom - self.zoom_speed, self.min_zoom)

    def smooth_zoom(self):
        previous_zoom = self.zoom_scale
        self.zoom_scale += (self.target_zoom - self.zoom_scale) * 0.05
        if self.zoom_scale != previous_zoom:
            mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
            before_zoom_offset = (mouse_pos - self.offset) / previous_zoom
            after_zoom_offset = (mouse_pos - self.offset) / self.zoom_scale
            self.offset += before_zoom_offset - after_zoom_offset

        # After zooming, re-constrain the camera to ensure it remains within bounds
        self.constrain_camera()

    def constrain_camera(self):
        # Get the dimensions of the display surface and ground rect
        screen_width, screen_height = self.display_surface.get_size()
        map_width, map_height = self.ground_rect.size

        # Calculate the maximum offset allowed based on the current zoom level
        max_offset_x = map_width * self.zoom_scale - screen_width
        max_offset_y = map_height * self.zoom_scale - screen_height

        # Constrain the offset to ensure the camera view stays within the map bounds
        self.offset.x = max(0, min(self.offset.x, max_offset_x / self.zoom_scale))
        self.offset.y = max(0, min(self.offset.y, max_offset_y / self.zoom_scale))

    def custom_draw(self):
        self.keyboard_control()
        self.zoom_keyboard_control()
        self.smooth_zoom()
        self.internal_surf.fill('#71ddee')
        ground_offset = (self.ground_rect.topleft - self.offset) * self.zoom_scale + self.internal_offset
        self.internal_surf.blit(self.ground_surf, ground_offset)
        scaled_surf = pygame.transform.scale(self.internal_surf, self.internal_surface_size_vector * self.zoom_scale)
        scaled_rect = scaled_surf.get_rect(center=(self.half_w, self.half_h))
        self.display_surface.blit(scaled_surf, scaled_rect)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

camera_group = CameraGroup()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            camera_group.target_zoom = min(max(camera_group.target_zoom + event.y * 0.1, camera_group.min_zoom), camera_group.max_zoom)

    screen.fill('#71ddee')
    camera_group.custom_draw()
    pygame.display.update()
    clock.tick(60)
