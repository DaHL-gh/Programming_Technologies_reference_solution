import sys

import time
import numpy as np
import moderngl as mgl
from PIL import Image
import pygame as pg
from pathlib import Path


class FractalGenerator:
    __vertices = np.array([[-1, 1.],
                           [-1, -1.],
                           [1, 1.],
                           [1, -1.]], dtype=np.float32)

    def __init__(self, fractal_shader: str, ctx: mgl.Context | None = None):
        if ctx is None:
            ctx = mgl.create_context(standalone=True)

        self._ctx = ctx
        self.vbo = self._ctx.buffer(self.__vertices)

        self.program = self._ctx.program(
            vertex_shader=Path("shader_templates/default.vert").read_text(),
            fragment_shader=fractal_shader)

        self.vao = self._ctx.vertex_array(self.program, [(self.vbo, '2f /v', 'in_position')])

        self.center = (0.0, 0.0)  # camera center
        self.scale = 1.0  # camera zoom
        self.iterations = 100  # number of iterations for the fractal

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value
        self.program['center'].value = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.program['scale'].value = value

    @property
    def iterations(self):
        return self._scale

    @iterations.setter
    def iterations(self, value):
        self._iterations = value
        self.program['iterations'].value = value

    def generate_fractal_to_file(self, width: int, height: int, output_path):
        start_time = time.time()

        target_texture = self._ctx.texture((width, height), 4, dtype="f4")
        fbo = self._ctx.framebuffer(color_attachments=target_texture)
        fbo.use()

        self.vao.render(mgl.TRIANGLE_STRIP)

        image = Image.fromarray(np.frombuffer(fbo.read(), dtype=np.uint8).reshape((height, width, 3)), 'RGB')
        image.save(output_path)

        target_texture.release()
        fbo.release()

        end_time = time.time()
        print(f"Generation execution time: {end_time - start_time:.4f} seconds (including saving)")
        print(
            f"Generation execution time for million pixels: {(end_time - start_time) / width / height * 10 ** 6:4f} seconds")

    def _generate_fractal_tile(self, width: int, height: int, offset_x: int, offset_y: int,
                               tile_size: int) -> np.ndarray:
        target_texture = self._ctx.texture((tile_size, tile_size), 4, dtype="f4")
        fbo = self._ctx.framebuffer(color_attachments=target_texture)
        fbo.use()

        scale_x = self.scale * 2.0 / width
        scale_y = self.scale * 2.0 / height

        tile_center_x = self.center[0] + (offset_x - width // 2) * scale_x
        tile_center_y = self.center[1] - (offset_y - height // 2) * scale_y
        self.program['center'].value = (tile_center_x, tile_center_y)
        self.program['scale'].value = self.scale * tile_size / max(width, height)

        self.vao.render(mgl.TRIANGLE_STRIP)

        tile_data = np.frombuffer(fbo.read(), dtype=np.uint8).reshape((tile_size, tile_size, 3))

        target_texture.release()
        fbo.release()

        return tile_data

    def generate_large_fractal(self, width: int, height: int, tile_size: int, output_path: str):
        start_time = time.time()

        large_image = Image.new('RGB', (width, height))

        for y in range(0, height, tile_size):
            for x in range(0, width, tile_size):
                print(f"Rendering tile at ({x}, {y})")

                current_tile_width = min(tile_size, width - x)
                current_tile_height = min(tile_size, height - y)

                tile = self._generate_fractal_tile(width, height, x, y, max(current_tile_width, current_tile_height))

                tile_image = Image.fromarray(tile, 'RGB')
                flipped_tile = tile_image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

                large_image.paste(flipped_tile.crop((0, 0, current_tile_width, current_tile_height)), (x, y))

        large_image.save(output_path)
        print(f"Fractal saved to {output_path}")

        end_time = time.time()
        print(f"Generation execution time: {end_time - start_time:.4f} seconds (including saving)")
        print(
            f"Generation execution time for million pixels: {(end_time - start_time) / width / height * 10 ** 6:4f} seconds")


class Window:
    def __init__(self, fractal_shader: str, window_size=(1000, 600)):
        pg.init()

        self.fps = 60
        self.clock = pg.time.Clock()
        self.size = window_size
        self.display = pg.display.set_mode(window_size, flags=pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)
        pg.display.set_caption("Fractal Camera Control")
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        self.ctx = mgl.create_context()

        self.fractal_generator = FractalGenerator(fractal_shader, self.ctx)

        self.pressed = []

    def handle_events(self):
        for key in self.pressed:
            fg = self.fractal_generator
            move = fg.scale / self.fps
            if key == pg.K_w:
                fg.center = (fg.center[0], fg.center[1] + move)
            if key == pg.K_s:
                fg.center = (fg.center[0], fg.center[1] - move)
            if key == pg.K_d:
                fg.center = (fg.center[0] + move, fg.center[1])
            if key == pg.K_a:
                fg.center = (fg.center[0] - move, fg.center[1])

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEWHEEL:
                if event.dict["y"] == 1:
                    self.fractal_generator.scale /= 1.1
                elif event.dict["y"] == -1:
                    self.fractal_generator.scale *= 1.1

            if event.type == pg.VIDEORESIZE:
                self.size = pg.display.get_window_size()

            if event.type == pg.KEYDOWN:
                self.pressed.append(event.dict["key"])

            if event.type == pg.KEYUP:
                self.pressed.remove(event.dict["key"])

                if event.dict["key"] == pg.K_F11:
                    self.size = pg.display.get_window_size()
                    pg.display.toggle_fullscreen()

    def draw(self):
        start_time = time.time()
        self.ctx.clear(0.0, 0.0, 0.0)

        fg = self.fractal_generator

        fg.vao.render(mgl.TRIANGLE_STRIP)

        pg.display.flip()

        end_time = time.time()
        print(f"draw execution time: {end_time - start_time:.4f} seconds")

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(self.fps)


if __name__ == "__main__":
    fs = Path("shader_templates/Mandelbrot.frag").read_text()

    # fg = FractalGenerator(fs)
    # fg.generate_large_fractal(50000, 50000, 2000, "large_output_image.png")

    # fg.generate_fractal_to_file(16000, 16000, "output_image.png")

    w = Window(fs)
    w.run()
