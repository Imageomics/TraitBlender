from .helpers import get_raup_apex
from .morphospace import ShellMorphospace, ShellMorphospaceSample
from .orientations import ORIENTATIONS

# Display name for GUI and config references. Folder name remains the internal identifier.
NAME = "Shell (Default)"

# Hyperparameters: Non-biological parameters (discretization, surface options). From config, not dataset.
# Regular traits (eps, h_0, etc.) are passed as sample() params from the dataset.
HYPERPARAMETERS = {
    'n_vertices_aperture': 20,  # Number of points around each shell ring (discretization)
    'time_step': 0.05,          # Time step for shell generation (discretization)
    'use_inner_surface': False, # Whether to generate inner surface with thickness
}

# The sampling function. It is called by the generate_morphospace_sample_op.
def sample(name="Shell", b=0.2, d=1.65, z=0, a=1, phi=0, psi=0, k=0,
           c_depth=0, c_n=70, n_depth=0, n=0, t=100,
           eps=0.8, h_0=0.1, S=5.0, hyperparameters=None):
    """
    Generate a shell sample using the Shell morphospace model (paper parameterization).

    Args:
        name (str): Name for the generated shell object
        b, d, z, a, phi, psi, k, c_depth, c_n, n_depth, n, t (float): Biological traits (from dataset)
        d (float): Horizontal distance scale (paper Eq. 2): r = d*e^(bt). From images (paper
            §2.4.3): d = (re+ri)/(re-ri)*a, with re/ri = axis to external/internal aperture border, a = ellipse ratio.
        k (float): Aperture displacement along the binormal in generating-curve units (Contreras §2.7.3).
            Positive for right valve, negative for left valve; 0 for most coiled shells.
        eps (float): Thickness parameter (allometric exponent) - trait
        h_0 (float): Base thickness parameter - trait
        S (float, optional): Aperture diameter in centimeters. If set, scale so aperture diameter = S cm. None = no scaling.
        hyperparameters (dict, optional): From config. n_vertices_aperture, time_step, use_inner_surface.
    """
    if hyperparameters is None:
        hyperparameters = {}
    merged_hyperparams = {
        **HYPERPARAMETERS,
        **{k: v for k, v in hyperparameters.items() if k in HYPERPARAMETERS},
    }

    morphospace = ShellMorphospace()
    return morphospace.generate_sample(
        name=name, b=b, d=d, z=z, a=a, phi=phi, psi=psi, k=k,
        c_depth=c_depth, c_n=c_n, n_depth=n_depth, n=n, t=t,
        eps=eps, h_0=h_0, S=S,
        **merged_hyperparams
    )

__all__ = ['NAME', 'sample', 'HYPERPARAMETERS', 'ORIENTATIONS', 'get_raup_apex']
