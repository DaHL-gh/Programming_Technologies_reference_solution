#version 330

in vec2 v_pos;
out fragColor vec4;

uniform vec2 center;
uniform float scale;
uniform int iterations;

#define AA 4  // Anti-aliasing factor

void main() {
    vec2 iResolution = vec2(10 * iterations);

    float ttlr = 0.0;
    float ttlr2 = 0.0;

    for (int m = 0; m < AA; m++)
    for (int n = 0; n < AA; n++) {

        #if AA > 1
        vec2 o = vec2(float(m), float(n)) / float(AA) - 0.5;
        vec3 z = vec3(((2.0 * (v_pos * iResolution.xy + o) - iResolution.xy) / iResolution.y) * scale,
                      0.0);
        #else
        vec3 z = vec3(((2.0 * v_pos - iResolution.xy) / iResolution.y) * scale,
                      0.0);
        #endif

        float dr = 1.0;
        float r2 = 0.0;

        for (int iter = 0; iter < 8; iter++) {
            z = clamp(z, -1.0, 1.0) * 2.0 - z;
            r2 = dot(z, z);
            if (r2 < 0.5) {
                float temp = 2.0;
                z *= temp;
                dr *= temp;
            } else if (r2 < 1.0) {
                float temp = 1.0 / r2;
                z *= temp;
                dr *= temp;
            }
            z = z * scale + vec3(center, 0.0);
            dr = dr * abs(scale) + 1.0;
        }

        ttlr += length(z) / abs(dr);
        ttlr2 += r2;
    }

    #if AA > 1
    float saa = float(AA * AA);
    ttlr /= saa;
    ttlr2 /= saa;
    #endif

    fragColor = vec4(vec3(sqrt(ttlr / ttlr2) * 10.0) * vec3(0.3, 1.0, 0.2), 1.0);
}