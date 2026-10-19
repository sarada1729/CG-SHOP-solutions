import matplotlib.pyplot as plt

from cgshop2027_pyutils.io import read_instance
from cgshop2027_pyutils.visualize import create_instance_plot

path = "test_instances1/fpg73_1k_1s2.instance.json"

instance = read_instance(path)

fig = create_instance_plot(instance)

plt.show()
