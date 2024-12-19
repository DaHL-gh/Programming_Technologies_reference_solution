#version 330

in vec2 in_position;

out vec2 v_pos;

void main() {
    v_pos = in_position;
    gl_Position = vec4(in_position, 0, 1);
}