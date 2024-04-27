import numpy as np
from bicycleparameters.models import Meijaard2007Model
from bicycleparameters.bicycle import ab_matrix


class SteerControlModel(Meijaard2007Model):
    """

    Tdel_total = -kphidot*phidot - kphi*phi + Tdel

    Tdel_total = -[kphi, kdelta, kphidot, kdeltadot] * x

    x = [roll angle,
         steer angle,
         roll rate,
         steer rate]

        The inputs are [roll torque,
                        steer torque]

    """

    def form_state_space_matrices(self, **parameter_overrides):
        """Returns the A and B matrices for the Whipple-Carvallo model
        linearized about the upright constant velocity configuration with a
        full state feedback steer controller.

        Returns
        =======
        A : ndarray, shape(4,4) or shape(n,4,4)
            The state matrix.
        B : ndarray, shape(4,2) or shape(n,4,2)
            The input matrix.

        Notes
        =====
        A, B, and K describe the model in state space form:

            x' = (A - B*K)*x + B*u

        where::

        x = |phi     | = |roll angle |
            |delta   |   |steer angle|
            |phidot  |   |roll rate  |
            |deltadot|   |steer rate |

        K = |0    0      0       0        |
            |kphi kdelta kphidot kdeltadot|

        u = |Tphi  | = |roll torque |
            |Tdelta|   |steer torque|

        """
        gain_names = ['kphi', 'kdelta', 'kphidot', 'kdeltadot']

        par, array_keys, array_len = self._parse_parameter_overrides(
            **parameter_overrides)

        # g, v, and the contoller gains are not used in the computation of M,
        # C1, K0, K2.

        M, C1, K0, K2 = self.form_reduced_canonical_matrices(
            **parameter_overrides)

        # steer controller gains, 2x4, no roll control
        if any(k in gain_names for k in array_keys):
            # if one of the gains is an array, create a set of gain matrices
            # where that single gain varies across the set
            K = np.array([[0.0, 0.0, 0.0, 0.0],
                          [par[p][0] if p in array_keys else par[p]
                           for p in gain_names]])
            # K is now shape(n, 2, 4)
            K = np.tile(K, (array_len, 1, 1))
            for k in array_keys:
                if k in gain_names:
                    K[:, 1, gain_names.index(k)] = par[k]
        else:  # gains are not an array
            K = np.array([[0.0, 0.0, 0.0, 0.0],
                          [par[p] for p in gain_names]])

        if array_keys:
            A = np.zeros((array_len, 4, 4))
            B = np.zeros((array_len, 4, 2))
            for i in range(array_len):
                Mi = M[i] if M.ndim == 3 else M
                C1i = C1[i] if C1.ndim == 3 else C1
                K0i = K0[i] if K0.ndim == 3 else K0
                K2i = K2[i] if K2.ndim == 3 else K2
                vi = par['v'] if np.isscalar(par['v']) else par['v'][i]
                gi = par['g'] if np.isscalar(par['g']) else par['g'][i]
                Ki = K[i] if K.ndim == 3 else K
                Ai, Bi = ab_matrix(Mi, C1i, K0i, K2i, vi, gi)
                A[i] = Ai - Bi@Ki
                B[i] = Bi
        else:  # scalar parameters
            A, B = ab_matrix(M, C1, K0, K2, par['v'], par['g'])
            A = A - B@K
            B = B

        return A, B
