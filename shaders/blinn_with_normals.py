import common
import OpenGL.GL as GL
from programs import SingletonProgram

vs_source = """
#version 430 core

uniform mat4 u_VP;

layout (location=0) in vec3 in_position_MS;
layout (location=1) in vec3 in_normal_MS;
layout (location=2) in vec3 in_ambient;
layout (location=3) in vec3 in_diffuse;
layout (location=4) in vec4 in_specular;
layout (location=5) in mat4 in_M;

layout (location=0) out vec3 out_position_WS;
layout (location=1) out vec3 out_ambient;
layout (location=2) out vec3 out_diffuse;
layout (location=3) out vec4 out_specular;
layout (location=4) out vec3 out_normal_WS;

void main()
{
    out_ambient = in_ambient;
    out_diffuse = in_diffuse;
    out_specular = in_specular;

    vec4 pos_WS = in_M * vec4(in_position_MS, 1.0);
    out_normal_WS = normalize(vec3(in_M * vec4(in_normal_MS, 0.0)));
    out_position_WS = vec3(pos_WS);
    gl_Position = u_VP * pos_WS;
}
"""

fs_source = """
#version 430 core

uniform vec3 u_lightDir_WS;
uniform vec3 u_eyePos_WS;

layout (location=0) in vec3 in_position_WS;
layout (location=1) in vec3 in_ambient;
layout (location=2) in vec3 in_diffuse;
layout (location=3) in vec4 in_specular;
layout (location=4) in vec3 in_normal_WS;

out vec4 out_colour;

void main()
{
    float diffuse = max(0.0, dot(in_normal_WS, u_lightDir_WS));
    vec3 toEye = normalize(u_eyePos_WS - in_position_WS);
    vec3 h = normalize(u_lightDir_WS + toEye);
    float specular = pow(max(0.0, dot(in_normal_WS, h)), in_specular.a);

    out_colour = vec4(in_ambient + in_diffuse*diffuse + in_specular.rgb*specular, 1.0);
}
"""

class BlinnWithNormalsProgram(SingletonProgram):
    def __init__(self):
        vs = common.compileShaderStage(vs_source, GL.GL_VERTEX_SHADER)
        fs = common.compileShaderStage(fs_source, GL.GL_FRAGMENT_SHADER)

        self.program = common.compileShaderProgram(vs, fs)

        self.attrib_position = GL.glGetAttribLocation(self.program, 'in_position_MS')
        self.attrib_normal = GL.glGetAttribLocation(self.program, 'in_normal_MS')
        self.attrib_ambient = GL.glGetAttribLocation(self.program, 'in_ambient')
        self.attrib_diffuse = GL.glGetAttribLocation(self.program, 'in_diffuse')
        self.attrib_specular = GL.glGetAttribLocation(self.program, 'in_specular')
        self.attrib_m = GL.glGetAttribLocation(self.program, "in_M")

        self.uniform_vp = GL.glGetUniformLocation(self.program, "u_VP")
        self.uniform_lightDir = GL.glGetUniformLocation(self.program, "u_lightDir_WS")
        self.uniform_eyePos = GL.glGetUniformLocation(self.program, "u_eyePos_WS")

