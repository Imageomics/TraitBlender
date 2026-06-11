import numpy as np
from .shell_morphospace_sample import ShellMorphospaceSample


class ShellMorphospace:

    def __init__(self):
        pass

    def _gamma(self, t, sin_t, cos_t, b, d, z):
        """Spiral centerline position."""
        return np.array([d * sin_t, d * cos_t, -z]) * np.exp(b * t)

    def _T(self, t, sin_t, cos_t, b, d, z):
        """Tangent vector component."""
        numerator = np.array([
            d * (b * sin_t + cos_t),
            d * (b * cos_t - sin_t),
            -b * z
        ])
        denominator = np.sqrt(d**2 * (b**2 + 1) + (b * z)**2)
        return numerator / denominator

    def _N(self, t, sin_t, cos_t, b):
        """Normal vector component."""
        numerator = np.array([b * cos_t - sin_t, -b * sin_t - cos_t, 0])
        denominator = np.sqrt(b**2 + 1)
        return numerator / denominator

    def _B(self, t, sin_t, cos_t, b, d, z):
        """Binormal vector component."""
        numerator = np.array([
            b * z * (b * sin_t + cos_t),
            b * z * (b * cos_t - sin_t),
            d * (b**2 + 1)
        ])
        denominator = np.sqrt((b**2 + 1) * (d**2 * (b**2 + 1) + b**2 * z**2))
        return numerator / denominator

    def _R_b(self, psi):
        """Rotation matrix used in the authors' notebook."""
        return np.array([
            [np.cos(psi), -np.sin(psi), 0],
            [np.sin(psi),  np.cos(psi), 0],
            [0, 0, 1]
        ])

    def _C(self, t, theta, sin_t, cos_t, sin_theta, cos_theta, b, a, d, z, phi, psi, k, c_n, c_depth, n, n_depth):
        """Aperture shape terms: (axial_ribs * spiral_ribs), aperture_size, aperture_shape."""
        aperture_size = np.exp(b * t) - (1 / (t + 1))

        # these are the lines I need to adjust when I get back
        axial_ribs = c_depth + 1 + c_depth * np.sin(c_n * t)
        spiral_ribs = n_depth + 1 + n_depth * np.sin(n * theta)

        normal = self._N(t, sin_t, cos_t, b)
        binormal = self._B(t, sin_t, cos_t, b, d, z)

        # This matches the Mathematica notebook's definition of A
        A = (
            ((a * np.cos(phi) * sin_theta) + (cos_theta * np.sin(phi))) * normal
            + ((-cos_theta * np.cos(phi)) + (a * sin_theta * np.sin(phi)) + k) * binormal
        )

        # The notebook uses A . RZ (row-vector times matrix), so use np.dot(A, RZ)
        rotation_matrix = self._R_b(psi)
        aperture_shape = np.dot(A, rotation_matrix)

        return (axial_ribs * spiral_ribs), aperture_size, aperture_shape

    def _lambda(self, t, theta, sin_t, cos_t, sin_theta, cos_theta, b, d, z, a, phi, psi, k, c_n, c_depth, n, n_depth, inner, eps, h_0):
        """Single point on shell surface (outer or inner)."""
        surface = self._C(
            t, theta, sin_t, cos_t, sin_theta, cos_theta,
            b, a, d, z, phi, psi, k, c_n, c_depth, n, n_depth
        )

        if inner:
            surface = surface[1] * surface[2]
            surface_norm = np.linalg.norm(surface)
            aperture_size_norm = np.exp(b * t) - (1 / (t + 1))
            thickness = (aperture_size_norm ** eps) * h_0

            # Numerical safeguards for inner surface thickness calculation.
            if surface_norm < 1e-10:
                surface_product = surface
            elif np.isnan(thickness) or np.isinf(thickness) or thickness < 0:
                surface_product = surface * 0.9
            elif thickness > surface_norm * 0.9:
                surface_product = surface * 0.1
            else:
                surface_product = surface * (1 - thickness / surface_norm)
        else:
            surface_product = surface[0] * surface[1] * surface[2]

        return self._gamma(t, sin_t, cos_t, b, d, z) + surface_product

    def _compute_surface_vertices(self, t_values, theta_values, sin_t_values, cos_t_values,
                                  sin_theta_values, cos_theta_values, b, d, z, a, phi, psi, k,
                                  c_n, c_depth, n, n_depth, eps, h_0, inner=False):
        """Compute full surface vertex array (outer or inner)."""
        return np.array([
            [
                self._lambda(
                    t, theta, sin_t, cos_t, sin_theta, cos_theta,
                    b, d, z, a, phi, psi, k, c_n, c_depth, n, n_depth, inner, eps, h_0
                )
                for theta, sin_theta, cos_theta in zip(theta_values, sin_theta_values, cos_theta_values)
            ]
            for t, sin_t, cos_t in zip(t_values, sin_t_values, cos_t_values)
        ])

    def generate_sample(self, name="Shell", b=0.2, d=1.65, z=0, a=1, phi=0, psi=0, k=0,
                        c_depth=0, c_n=70, n_depth=0, n=0, t=100,
                        n_vertices_aperture=40, time_step=1/30, use_inner_surface=True,
                        eps=0.8, h_0=0.1, S=5.0):
        """Generate a shell sample.

        The outer-surface formula is matched as closely as possible to the authors'
        Mathematica notebook. Extra options like inner surface thickness and global
        scaling are retained from your version.
        """

        t_values = np.arange(0, t, time_step)
        if t_values.size == 0 or t_values[-1] != t:
            t_values = np.append(t_values, t)
        theta_values = np.linspace(0, 2 * np.pi, n_vertices_aperture, endpoint=False)

        sin_t_values = np.sin(t_values)
        cos_t_values = np.cos(t_values)
        sin_theta_values = np.sin(theta_values)
        cos_theta_values = np.cos(theta_values)

        outer_surface = self._compute_surface_vertices(
            t_values, theta_values, sin_t_values, cos_t_values,
            sin_theta_values, cos_theta_values, b, d, z, a, phi, psi, k,
            c_n, c_depth, n, n_depth, eps, h_0, inner=False
        )

        if use_inner_surface:
            inner_surface = self._compute_surface_vertices(
                t_values, theta_values, sin_t_values, cos_t_values,
                sin_theta_values, cos_theta_values, b, d, z, a, phi, psi, k,
                c_n, c_depth, n, n_depth, eps, h_0, inner=True
            )
            aperture = np.vstack((outer_surface[-1], inner_surface[-1]))
        else:
            inner_surface = None
            aperture = outer_surface[-1]

        # Optional size scaling retained from your version.
        if S is not None and np.isfinite(S):
            g_tf = np.exp(b * t) - 1 / (t + 1)
            B_amplitude = np.sqrt((a * np.sin(phi)) ** 2 + (np.cos(phi)) ** 2)
            D_B = 2.0 * g_tf * B_amplitude
            if D_B > 0:
                S_m = S / 100.0
                s_f = S_m / D_B
                outer_surface = outer_surface * s_f
                if inner_surface is not None:
                    inner_surface = inner_surface * s_f
                aperture = aperture * s_f

        shell = {
            "outer_surface": outer_surface,
            "inner_surface": inner_surface,
            "aperture": aperture,
        }

        return ShellMorphospaceSample(name=name, data=shell)