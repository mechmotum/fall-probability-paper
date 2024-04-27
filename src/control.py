import os

from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
from bicycleparameters.bicycle import sort_eigenmodes
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import golden_ratio

#from data import bike_with_rider as bike_par
from data import bike_without_rider as bike_par
#from data import rigid_bike_without_rider as bike_par
from model import SteerControlModel

SCRIPT_PATH = os.path.realpath(__file__)
SRC_DIR = os.path.dirname(SCRIPT_PATH)
ROOT_DIR = os.path.realpath(os.path.join(SRC_DIR, '..'))
FIG_DIR = os.path.join(ROOT_DIR, 'figures')
KPH2MPS = 1000.0/3600.0

if not os.path.exists(FIG_DIR):
    os.mkdir(FIG_DIR)

parameter_set = Meijaard2007ParameterSet(bike_par, True)
model = SteerControlModel(parameter_set)

# FIGURE : Geometry and mass distribution
fig, ax = plt.subplots()
fig.set_size_inches((5.0, 5.0/golden_ratio))
parameter_set.plot_all(ax=ax)
fig.savefig(os.path.join(FIG_DIR, 'bicycle-geometry-mass.png'), dpi=300)


def stable_ranges(speeds, evals):
    where_stable = np.all(evals.real < 0.0, axis=1)
    number_ranges = np.count_nonzero(np.diff(where_stable)) - 1
    stable_speeds = speeds[where_stable]
    if number_ranges == 1:
        ranges = ((stable_speeds[0], stable_speeds[-1]),)
    else:
        # TODO
        #idxs = np.argmax(np.abs(np.diff(where_stable)))
        ranges = ((stable_speeds[0], stable_speeds[-1]),)
    return ranges


# FIGURE : Compare eigenvalues vs speed for uncontrolled.
fig, ax = plt.subplots()
fig.set_size_inches((3.0, 3.0/golden_ratio))
speeds = np.linspace(0.0, 10.0, num=1001)
evals_, evecs_ = sort_eigenmodes(*model.calc_eigen(v=speeds))
weave_idx = np.argmin(np.abs(evals_[:, -1].real))
weave_speed, capsize_speed = stable_ranges(speeds, evals_)[0]
print('Uncontrolled weave speed: {:1.2f} [m/s]'.format(weave_speed))
print('Uncontrolled capsize speed: {:1.2f} [m/s]'.format(capsize_speed))
ax.axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
ax.axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
ax = model.plot_eigenvalue_parts(ax=ax, v=speeds, colors=['k']*4)
ax.fill_between(speeds, -10, 10,
                where=(speeds > weave_speed) & (speeds < capsize_speed),
                color='green', alpha=0.5, transform=ax.get_xaxis_transform())
ax.set_ylim((-10, 10))
ax.set_ylabel('')
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR,
                         'uncontrolled-eig-vs-speeds.png'),
            dpi=300)

fig, ax = plt.subplots()
fig.set_size_inches((3.0, 3.0/golden_ratio))
# TODO : This finds the uncontrolled weave speed for the controller design, but
# the actual bike uses a specific value based on the benchmark bike values
# (probably).
kphidots = -10.0*(weave_speed - speeds)
kphidots[weave_idx:] = 0.0
evals_, evecs_ = sort_eigenmodes(*model.calc_eigen(v=speeds, kphidot=kphidots))
weave_speed, capsize_speed = stable_ranges(speeds, evals_)[0]
print('Controlled (gain=-8.0) weave speed: {:1.2f} [m/s]'.format(weave_speed))
print('Controlled (gain=-8.0) capsize speed: {:1.2f} [m/s]'.format(capsize_speed))
ax = model.plot_eigenvalue_parts(ax=ax, v=speeds, kphidot=kphidots,
                                 colors=['k']*4)
ax.axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
ax.axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
ax.fill_between(speeds, -10, 10,
                where=(speeds > weave_speed) & (speeds < capsize_speed),
                color='green', alpha=0.5, transform=ax.get_xaxis_transform())
ax.set_ylim((-10, 10))
ax.set_ylabel('')
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR,
                         'balance-assist-controllers-eig-vs-speeds.png'),
            dpi=300)

# FIGURE : Plot the roll rate gains versus speed.
fig, ax = plt.subplots()
fig.set_size_inches((3.0, 3.0/golden_ratio))
ax.plot(speeds, kphidots)
ax.set_ylabel(r'$k_\dot{\phi}$')
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'gains-vs-speed.png'), dpi=300)


# FIGURE : Simulate an initial value problem at a low speed under control.
idx = 170  # 6 km/h


def controller(t, x):
    K = np.array([[0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, kphidots[idx], 0.0]])
    torques = -K@x
    if np.abs(torques[1]) >= 7.0:
        torques[1] = np.sign(torques[1])*7.0
    return torques


times = np.linspace(0.0, 10.0, num=1001)
x0 = np.deg2rad([5.0, -5.0, 0.0, 0.0])
axes = model.plot_simulation(times, x0, input_func=controller, v=speeds[idx])
axes[0].set_title(r'$v$ = {:1.2f} [m/s]'.format(speeds[idx]))
axes[0].set_ylabel('Torque\n[Nm]')
axes[1].set_ylabel('Angle\n[deg]')
axes[2].set_ylabel('Angular Rate\n[deg/s]')
fig = axes[0].figure
fig.set_size_inches((6.0, 6.0/golden_ratio))
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'pd-simulation.png'), dpi=300)
