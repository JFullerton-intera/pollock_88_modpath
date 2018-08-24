import flopy
import numpy as np
import matplotlib.pyplot as plt
import flopy.utils.binaryfile as bf
import os

#note: change the version from modflow 2005 to mf2k. Guessed at the version code, because I couldn't figure out the help
modelname = 'test_1'
exe = os.path.join("../gw_codes",'mf2k-chprc08spl.exe') # moved the exes here for clean up, RKK
model_ws = os.path.join('workspace') # moved model here to keep things orginized, RKK
mf = flopy.modflow.Modflow(modelname, version='mf2k', exe_name =exe,model_ws=model_ws)
#m = flopy.modflow.Modflow.add_output_file(self=mf, unit=50, fname=modelname, extension='.cbb', binflag=True)

#DIS
Lx = 40000.
Ly = 40000./2
ztop = 200.
zbot = 0
nlay = 1
nrow = int(400)
ncol = 400*2
delr = Lx/ncol
delc = Ly/nrow
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
nper = 10 # lets add some more stress periods, RKK
perlen = 1

print(ncol)
dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm[1:],nper=nper,perlen=perlen)

#BAS for 64-bit
ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
ibound[:, :, 0] = -1
ibound[:, :, -1] = -1
strt = np.ones((nlay, nrow, ncol), dtype=np.float32)
strt[:, :, 0] = 200.
strt[:, :, -1] = 167.35
bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)

#LPF change hydraulic conductivity here
lpf = flopy.modflow.ModflowLpf(mf, hk=10, vka=10., ipakcb=53)

#OC
spd = {} # slight change to oc so we can save heads and budget for all stress periods
for sp in range(nper):
    spd[(sp, 0)] = ['print head', 'print budget', 'save head', 'save budget']
oc = flopy.modflow.ModflowOc(mf, stress_period_data=spd, compact=True)
#, extension=['oc', 'hds', 'ddn', 'cbb', 'ibo']

#PCG
#I've seen examples of all three solvers being used
pcg = flopy.modflow.ModflowPcg(mf)

#WEL
Qgpm = -150
Qcfd = Qgpm * (60*24) / 7.4018
wel_spd = {0:[0,int(nrow/2),int(310*2),Qcfd]}
wel = flopy.modflow.ModflowWel(mf,stress_period_data=wel_spd,ipakcb=53)

#write the modflow input files
mf.write_input()

# Run the MODFLOW model
success, buff = mf.run_model(silent=False)

plt.subplot(1,1,1,aspect='equal')
hds = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
times = hds.get_times()
head = hds.get_data(totim=times[-1])
levels = np.arange(1,10,1)
extent = (delr/2., Lx - delr/2., Ly - delc/2., delc/2)
plt.contour(head[0, :, :], levels=levels, extent=extent)
plt.savefig('test_1.png')

fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(1, 1, 1, aspect='equal')

hds = bf.HeadFile(os.path.join(model_ws,modelname+'.hds'))
head = hds.get_data(totim=times[-1])
levels = np.linspace(0, 10, 11)

cbb = bf.CellBudgetFile(os.path.join(model_ws,modelname+'.cbc'))
kstpkper_list = cbb.get_kstpkper()
frf = cbb.get_data(text='FLOW RIGHT FACE', totim=times[-1])[0]
fff = cbb.get_data(text='FLOW FRONT FACE', totim=times[-1])[0]

modelmap = flopy.plot.ModelMap(model=mf, layer=0)
qm = modelmap.plot_ibound()
lc = modelmap.plot_grid()
cs = modelmap.contour_array(head, levels=levels)
quiver = modelmap.plot_discharge(frf, fff, head=head)
plt.savefig('test_1b.png')

# import test_1_mp