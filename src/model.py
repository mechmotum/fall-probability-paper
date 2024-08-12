import numpy as np
import matplotlib.pyplot as plt
from bicycleparameters.models import Meijaard2007Model
from bicycleparameters.bicycle import ab_matrix, sort_eigenmodes


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

    def plot_eigenvalue_parts(self, ax=None, colors=None,
                              show_stable_regions=True, hide_zeros=False,
                              **parameter_overrides):
        """Returns a matplotlib axis of the real and imaginary parts of the
        eigenvalues plotted against the provided parameter.

        Parameters
        ==========
        ax : Axes
            Matplotlib axes.
        colors : sequence, len(4)
            Matplotlib colors for the 4 modes.
        show_stable_regions : boolean, optional
            If true, a grey shaded background will indicate stable regions.
        hide_zeros : boolean or float, optional
            If true, real or imaginary parts that are smaller than 1e-12 will
            not be plotted. Providing a float will set the tolerance.
        **parameter_overrides : dictionary
            Parameter keys that map to floats or array_like of floats
            shape(n,). All keys that map to array_like must be of the same
            length.

        Examples
        ========

        .. plot::
           :include-source: True
           :context: reset

           import numpy as np
           from bicycleparameters.parameter_dicts import meijaard2007_browser_jason
           from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
           from bicycleparameters.models import Meijaard2007Model
           p = Meijaard2007ParameterSet(meijaard2007_browser_jason, True)
           m = Meijaard2007Model(p)
           m.plot_eigenvalue_parts(v=np.linspace(0.0, 10.0, num=101))

        """

        if ax is None:
            fig, ax = plt.subplots()

        evals, evecs = self.calc_eigen(**parameter_overrides)
        if len(evals.shape) > 1:
            evals, evecs = sort_eigenmodes(evals, evecs)
        else:
            evals, evecs = np.array([evals]), np.array([evecs])

        tol = hide_zeros if isinstance(hide_zeros, float) else 1e-12

        par, array_keys, _ = self._parse_parameter_overrides(
            **parameter_overrides)

        if colors is None:
            colors = ['C0', 'C1', 'C2', 'C3']
        legend = ['Mode 1', 'Mode 2', 'Mode 3', 'Mode 4',
                  'Mode 1', 'Mode 2', 'Mode 3', 'Mode 4']

        if show_stable_regions:
            ax.fill_between(par[array_keys[0]],
                            np.min([np.min(evals.real), np.min(evals.imag)]),
                            np.max([np.max(evals.real), np.max(evals.imag)]),
                            where=np.all(evals.real < 0.0, axis=1),
                            color='grey',
                            alpha=0.25,
                            transform=ax.get_xaxis_transform())

        # imaginary components
        for eval_sequence, color, label in zip(evals.T, colors, legend):
            imag_vals = np.abs(np.imag(eval_sequence))
            if hide_zeros:
                imag_vals[np.abs(imag_vals) < tol] = np.nan
            ax.plot(par[array_keys[0]], imag_vals, color=color, label=label,
                    linestyle='--')

        # plot the real parts of the eigenvalues
        for eval_sequence, color, label in zip(evals.T, colors, legend):
            real_vals = np.real(eval_sequence)
            if hide_zeros:
                real_vals[np.abs(real_vals) < tol] = np.nan
            ax.plot(par[array_keys[0]], real_vals, color=color, label=label)

        # set labels and limits
        ax.set_ylabel('Real and Imaginary Parts of the Eigenvalue [1/s]')
        ax.set_xlim((par[array_keys[0]][0], par[array_keys[0]][-1]))

        ax.grid()

        ax.set_xlabel(array_keys[0])

        return ax
