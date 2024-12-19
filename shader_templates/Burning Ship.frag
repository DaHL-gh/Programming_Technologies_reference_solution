#version 330

in vec2 v_pos;
out fragColor vec4;

uniform vec2 center;
uniform float scale;
uniform int iterations;

void main() {
    vec2 z = v_pos * scale + center;
    vec2 c = z;
    int iter;
    for (iter = 0; iter < iterations; iter++) {
        if (dot(z, z) > 4.0) break;
        z = vec2(abs(z.x) * abs(z.x) - abs(z.y) * abs(z.y), 2.0 * abs(z.x) * abs(z.y)) + c;
    }
    float color = float(iter) / float(iterations);
    fragColor = vec4(color * 0.8, color * 0.4, color * 0.1, 1.0);
}
