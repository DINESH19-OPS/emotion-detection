// Aurora WebGL Component (Vanilla JS)
// Uses OGL library for WebGL rendering

const VERT = `#version 300 es
in vec2 position;
void main() {
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const FRAG = `#version 300 es
precision highp float;

uniform float uTime;
uniform float uAmplitude;
uniform vec3 uColorStops[3];
uniform vec2 uResolution;
uniform float uBlend;

out vec4 fragColor;

vec3 permute(vec3 x) {
  return mod(((x * 34.0) + 1.0) * x, 289.0);
}

float snoise(vec2 v){
  const vec4 C = vec4(
      0.211324865405187, 0.366025403784439,
      -0.577350269189626, 0.024390243902439
  );
  vec2 i  = floor(v + dot(v, C.yy));
  vec2 x0 = v - i + dot(i, C.xx);
  vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
  vec4 x12 = x0.xyxy + C.xxzz;
  x12.xy -= i1;
  i = mod(i, 289.0);

  vec3 p = permute(
      permute(i.y + vec3(0.0, i1.y, 1.0))
    + i.x + vec3(0.0, i1.x, 1.0)
  );

  vec3 m = max(
      0.5 - vec3(
          dot(x0, x0),
          dot(x12.xy, x12.xy),
          dot(x12.zw, x12.zw)
      ), 
      0.0
  );
  m = m * m;
  m = m * m;

  vec3 x = 2.0 * fract(p * C.www) - 1.0;
  vec3 h = abs(x) - 0.5;
  vec3 ox = floor(x + 0.5);
  vec3 a0 = x - ox;
  m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);

  vec3 g;
  g.x  = a0.x  * x0.x  + h.x  * x0.y;
  g.yz = a0.yz * x12.xz + h.yz * x12.yw;
  return 130.0 * dot(m, g);
}

struct ColorStop {
  vec3 color;
  float position;
};

void main() {
  vec2 uv = gl_FragCoord.xy / uResolution;
  
  vec3 color0 = uColorStops[0];
  vec3 color1 = uColorStops[1];
  vec3 color2 = uColorStops[2];
  
  vec3 rampColor;
  if (uv.x < 0.5) {
    float t = uv.x * 2.0;
    rampColor = mix(color0, color1, t);
  } else {
    float t = (uv.x - 0.5) * 2.0;
    rampColor = mix(color1, color2, t);
  }
  
  float height = snoise(vec2(uv.x * 2.0 + uTime * 0.1, uTime * 0.25)) * 0.5 * uAmplitude;
  height = exp(height);
  height = (uv.y * 2.0 - height + 0.2);
  float intensity = 0.6 * height;
  
  float midPoint = 0.20;
  float auroraAlpha = smoothstep(midPoint - uBlend * 0.5, midPoint + uBlend * 0.5, intensity);
  
  vec3 auroraColor = intensity * rampColor;
  
  fragColor = vec4(auroraColor * auroraAlpha, auroraAlpha);
}
`;

class Aurora {
  constructor(container, options = {}) {
    this.container = container;
    this.options = {
      colorStops: ['#5227FF', '#7cff67', '#5227FF'],
      amplitude: 1.0,
      blend: 0.5,
      speed: 1.0,
      ...options
    };

    this.animateId = null;
    this.canvas = null;
    this.gl = null;
    this.program = null;
    this.vao = null;
    this.vertexBuffer = null;

    this.init();
  }

  init() {
    const canvas = document.createElement('canvas');
    this.canvas = canvas;
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    this.container.appendChild(canvas);

    const gl = canvas.getContext('webgl2', {
      alpha: true,
      premultipliedAlpha: true,
      antialias: true
    });
    this.gl = gl;

    gl.clearColor(0, 0, 0, 0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    this.createProgram();
    this.createGeometry();
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  createProgram() {
    const gl = this.gl;

    const vertShader = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vertShader, VERT);
    gl.compileShader(vertShader);
    if (!gl.getShaderParameter(vertShader, gl.COMPILE_STATUS)) {
      console.error('Vertex shader error:', gl.getShaderInfoLog(vertShader));
    }

    const fragShader = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fragShader, FRAG);
    gl.compileShader(fragShader);
    if (!gl.getShaderParameter(fragShader, gl.COMPILE_STATUS)) {
      console.error('Fragment shader error:', gl.getShaderInfoLog(fragShader));
    }

    const program = gl.createProgram();
    gl.attachShader(program, vertShader);
    gl.attachShader(program, fragShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program));
    }

    this.program = program;
    gl.useProgram(program);

    this.uniforms = {
      uTime: gl.getUniformLocation(program, 'uTime'),
      uAmplitude: gl.getUniformLocation(program, 'uAmplitude'),
      uColorStops: gl.getUniformLocation(program, 'uColorStops'),
      uResolution: gl.getUniformLocation(program, 'uResolution'),
      uBlend: gl.getUniformLocation(program, 'uBlend')
    };

    this.updateUniforms();
  }

  createGeometry() {
    const gl = this.gl;
    const positions = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
       1,  1
    ]);

    this.vertexBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

    const positionLocation = gl.getAttribLocation(this.program, 'position');
    this.vao = gl.createVertexArray();
    gl.bindVertexArray(this.vao);
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
  }

  hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? [
      parseInt(result[1], 16) / 255,
      parseInt(result[2], 16) / 255,
      parseInt(result[3], 16) / 255
    ] : [1, 1, 1];
  }

  updateUniforms() {
    const gl = this.gl;
    const colors = this.options.colorStops.map(hex => this.hexToRgb(hex));

    gl.uniform1f(this.uniforms.uTime, 0);
    gl.uniform1f(this.uniforms.uAmplitude, this.options.amplitude);
    gl.uniform1f(this.uniforms.uBlend, this.options.blend);
    gl.uniform2f(this.uniforms.uResolution, this.canvas.width, this.canvas.height);
    gl.uniform3fv(this.uniforms.uColorStops, new Float32Array(colors.flat()));
  }

  resize() {
    const gl = this.gl;
    const width = this.container.offsetWidth;
    const height = this.container.offsetHeight;

    this.canvas.width = width;
    this.canvas.height = height;

    gl.viewport(0, 0, width, height);
    gl.uniform2f(this.uniforms.uResolution, width, height);
  }

  animate(t) {
    this.animateId = requestAnimationFrame((t) => this.animate(t));

    const gl = this.gl;
    const time = t * 0.01 * this.options.speed;

    gl.uniform1f(this.uniforms.uTime, time * 0.1);
    gl.uniform1f(this.uniforms.uAmplitude, this.options.amplitude);
    gl.uniform1f(this.uniforms.uBlend, this.options.blend);

    gl.bindVertexArray(this.vao);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }

  destroy() {
    if (this.animateId) {
      cancelAnimationFrame(this.animateId);
    }
    if (this.canvas && this.canvas.parentNode) {
      this.canvas.parentNode.removeChild(this.canvas);
    }
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Aurora;
}
