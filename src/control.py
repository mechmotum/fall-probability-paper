import os

from bicycleparameters.parameter_sets import Meijaard2007ParameterSet
from bicycleparameters.bicycle import sort_eigenmodes
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import golden_ratio

from data import bike_with_rider, bike_without_rider
from model import SteerControlModel

SCRIPT_PATH = os.path.realpath(__file__)
SRC_DIR = os.path.dirname(SCRIPT_PATH)
ROOT_DIR = os.path.realpath(os.path.join(SRC_DIR, '..'))
FIG_DIR = os.path.join(ROOT_DIR, 'figures')
KPH2MPS = 1000.0/3600.0
MPS2KPH = 1.0/KPH2MPS

if not os.path.exists(FIG_DIR):
    os.mkdir(FIG_DIR)

par_set_with = Meijaard2007ParameterSet(bike_with_rider, True)
model_with = SteerControlModel(par_set_with)

par_set_without = Meijaard2007ParameterSet(bike_without_rider, False)
model_without = SteerControlModel(par_set_without)

# FIGURE : Geometry and mass distribution
fig, axes = plt.subplots(1, 2, sharey=True, layout='compressed')
fig.set_size_inches((160/25.4, 160/25.4/golden_ratio))
par_set_without.plot_all(ax=axes[0])
par_set_with.plot_all(ax=axes[1])
fig.savefig(os.path.join(FIG_DIR, 'bicycle-with-geometry-mass.png'), dpi=300)

speeds = np.linspace(0.0, 10.0, num=2001)

# control law
vmin, vmin_idx = 1.5, np.argmin(np.abs(speeds - 1.5))
vmax, vmax_idx = 4.7, np.argmin(np.abs(speeds - 4.7))
kphidots = -10.0*(vmax - speeds)
kphidots[:vmin_idx] = -10.0*(vmax - vmin)/vmin*speeds[:vmin_idx]
kphidots[vmax_idx:] = 0.0

# FIGURE : Plot the roll rate gains versus speed.
fig, ax = plt.subplots(layout='compressed')
fig.set_size_inches((80/25.4, 80/25.4/golden_ratio))
ax.plot(speeds, kphidots)
ax.set_ylabel(r'$k_\dot{\phi}$')
fig.savefig(os.path.join(FIG_DIR, 'gains-vs-speed.png'), dpi=300)

# FIGURE : Compare eigenvalues vs speed for uncontrolled.


def stable_ranges(evals):
    # TODO : This should return the indice after a rise and before a fall. It
    # now always returns the indices after a rise or fall.
    where_stable = np.all(evals.real < 0.0, axis=1)
    padded = np.hstack(([False], where_stable, [False]))
    start_stop_idxs = np.flatnonzero(np.diff(padded))
    return start_stop_idxs.reshape(-1, 2)


fig_four, axes = plt.subplots(2, 2, sharex=True, sharey=True,
                              layout='compressed')
fig.set_size_inches((160/25.4, 160/25.4/golden_ratio))

evals_, evecs_ = sort_eigenmodes(*model_without.calc_eigen(v=speeds))
weave_idx, capsize_idx = stable_ranges(evals_)[0]
weave_speed, capsize_speed = speeds[weave_idx], speeds[capsize_idx]
print('Uncontrolled weave speed: {:1.2f} [m/s]'.format(weave_speed))
print('Uncontrolled capsize speed: {:1.2f} [m/s]'.format(capsize_speed))
axes[0, 0].axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[0, 0].axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
model_without.plot_eigenvalue_parts(ax=axes[0, 0], v=speeds, colors=['k']*4)
axes[0, 0].fill_between(speeds, -10, 10,
                        where=np.all(evals_.real < 0.0, axis=1),
                        color='green', alpha=0.4,
                        transform=axes[0, 0].get_xaxis_transform())
axes[0, 0].set_title('Without Rider')
axes[0, 0].set_ylim((-10, 10))
axes[0, 0].set_ylabel('Eigenvalue Components [1/s]')
axes[0, 0].set_xlabel('')

evals_, evecs_ = sort_eigenmodes(*model_without.calc_eigen(v=speeds,
                                                           kphidot=kphidots))
for ranges in stable_ranges(evals_):
    weave_speed = speeds[ranges[0]]
    capsize_speed = speeds[ranges[1]]
    msg = 'Controlled (gain=-10.0) lower speed: {:1.2f} [m/s]'
    print(msg.format(weave_speed))
    msg = 'Controlled (gain=-10.0) upped speed: {:1.2f} [m/s]'
    print(msg.format(capsize_speed))
model_without.plot_eigenvalue_parts(ax=axes[1, 0], v=speeds, kphidot=kphidots,
                                    colors=['k']*4)
axes[1, 0].axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[1, 0].axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[1, 0].fill_between(speeds, -10, 10,
                        where=np.all(evals_.real < 0.0, axis=1),
                        color='green', alpha=0.4,
                        transform=axes[1, 0].get_xaxis_transform())
axes[1, 0].set_ylim((-10, 10))
axes[1, 0].set_ylabel('Eigenvalue Components [1/s]')
axes[1, 0].set_xlabel('Speed [m/s]')

evals_, evecs_ = sort_eigenmodes(*model_with.calc_eigen(v=speeds))
evals_save = evals_
weave_idx, capsize_idx = stable_ranges(evals_)[0]
weave_speed = speeds[weave_idx]
capsize_speed = speeds[capsize_idx]
print('Uncontrolled weave speed: {:1.2f} [m/s]'.format(weave_speed))
print('Uncontrolled capsize speed: {:1.2f} [m/s]'.format(capsize_speed))
axes[0, 1].axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[0, 1].axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
model_with.plot_eigenvalue_parts(ax=axes[0, 1], v=speeds, colors=['k']*4)
axes[0, 1].fill_between(speeds, -10, 10,
                        where=np.all(evals_.real < 0.0, axis=1),
                        color='green', alpha=0.4,
                        transform=axes[0, 1].get_xaxis_transform())
axes[0, 1].set_title('With Rider')
axes[0, 1].set_ylim((-10, 10))
axes[0, 1].set_ylabel('')
axes[0, 1].set_xlabel('')

evals_, evecs_ = sort_eigenmodes(*model_with.calc_eigen(v=speeds,
                                                        kphidot=kphidots))
evals_[weave_idx:] = evals_save[weave_idx:]
for ranges in stable_ranges(evals_):
    weave_speed = speeds[ranges[0]]
    capsize_speed = speeds[ranges[1]]
    msg = 'Controlled (gain=-10.0) lower speed: {:1.2f} [m/s]'
    print(msg.format(weave_speed))
    msg = 'Controlled (gain=-10.0) upped speed: {:1.2f} [m/s]'
    print(msg.format(capsize_speed))
model_with.plot_eigenvalue_parts(ax=axes[1, 1], v=speeds, kphidot=kphidots,
                                 colors=['k']*4)
axes[1, 1].axvline(6.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[1, 1].axvline(10.0*KPH2MPS, ymin=-10.0, ymax=10.0)
axes[1, 1].fill_between(speeds, -10, 10,
                        where=np.all(evals_.real < 0.0, axis=1),
                        color='green', alpha=0.4,
                        transform=axes[1, 1].get_xaxis_transform())
axes[1, 1].set_ylim((-10, 10))
axes[1, 1].set_ylabel('')
axes[1, 1].set_xlabel('Speed [m/s]')

fig_four.savefig(os.path.join(FIG_DIR, 'balance-assist-eig-vs-speeds.png'),
                 dpi=300)


# FIGURE : Simulate an initial value problem at a low speed under control.
idx = np.argmin(np.abs(speeds - 6.0*KPH2MPS))  # 6 km/h


def controller(t, x):
    K = np.array([[0.0, 0.0, 0.0, 0.0],
                  [0.0, 0.0, kphidots[idx], 0.0]])
    torques = -K@x
    if np.abs(torques[1]) >= 7.0:
        torques[1] = np.sign(torques[1])*7.0
    return torques


times = np.linspace(0.0, 10.0, num=1001)
x0 = np.deg2rad([10.0, -10.0, 0.0, 0.0])
axes = model_without.plot_simulation(times, x0, input_func=controller,
                                     v=speeds[idx])
axes[0].set_title(r'$v$ = {:1.2f} [m/s]'.format(speeds[idx]))
axes[0].set_ylabel('Torque\n[Nm]')
axes[1].set_ylabel('Angle\n[deg]')
axes[2].set_ylabel('Angular Rate\n[deg/s]')
fig = axes[0].figure
fig.set_size_inches((6.0, 6.0/golden_ratio))
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, 'pd-simulation.png'), dpi=300)
