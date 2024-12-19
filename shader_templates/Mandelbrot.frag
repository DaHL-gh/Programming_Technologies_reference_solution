#version 330

in vec2 v_pos;
out vec4 fragColor;

uniform vec2 center;
uniform float scale;
uniform int iterations;

void main() {
    vec2 z = v_pos * scale + center;
    vec2 c = z;
    int iter;

    for (iter = 0; iter < iterations; iter++) {
        if (dot(z, z) > 4.0) break;
        z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
    }

    float color = float(iter) / float(iterations);
    fragColor = vec4(color, color * 0.5, color * 0.25, 1.0);
}