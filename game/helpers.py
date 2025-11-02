add_vecs = lambda v1, v2: [v1[0] + v2[0], v1[1] + v2[1]]
sub_vecs = lambda v1, v2: [v1[0] - v2[0], v1[1] - v2[1]]
mult_vec_float = lambda v, scalar: [v[0] * scalar, v[1] * scalar]
div_vec_float = lambda v, scalar: [v[0] / scalar, v[1] / scalar]
clamp = lambda val, min_val, max_val: max(min(val, max_val), min_val)
def lerp(a, b, t):
    return a + (b - a) * t