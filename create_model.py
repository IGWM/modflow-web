import flopy
import os
import matplotlib.pyplot as plt
import platform

def create_simple_model():
    # Set up the model
    model_name = "simple_model"
    model_ws = "./model_files"
    os.makedirs(model_ws, exist_ok=True)

    # Determine the correct executable name based on the operating system
    if platform.system() == "Windows":
        mf6_exe = "mf6.exe"
    else:
        mf6_exe = "mf6"

    # Create the MODFLOW 6 simulation
    sim = flopy.mf6.MFSimulation(sim_name=model_name, sim_ws=model_ws, exe_name=mf6_exe)

    # Define the time discretization before other packages
    tdis = flopy.mf6.ModflowTdis(sim, nper=1, perioddata=[(1.0, 1, 1.0)])

    # Create the MODFLOW 6 groundwater flow model
    gwf = flopy.mf6.ModflowGwf(sim, modelname=model_name, save_flows=True)

    # Add the solver
    ims = flopy.mf6.ModflowIms(sim, print_option='SUMMARY', complexity='SIMPLE')

    # Define the discretization
    nlay, nrow, ncol = 1, 10, 10
    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=100,
        delc=100,
        top=0,
        botm=-50,
    )

    # Define the initial conditions
    ic = flopy.mf6.ModflowGwfic(gwf, strt=0)

    # Define the node property flow
    npf = flopy.mf6.ModflowGwfnpf(gwf, icelltype=1, k=1.0)

    # Define the storage
    sto = flopy.mf6.ModflowGwfsto(gwf, ss=1e-5, sy=0.1, transient={0: True})

    # Define the constant head boundaries
    chd_spd = []
    for row in range(nrow):
        chd_spd.append([(0, row, 0), 0.0])
        chd_spd.append([(0, row, ncol-1), 10.0])
    chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=chd_spd)

    # Define the output control
    oc = flopy.mf6.ModflowGwfoc(
        gwf,
        head_filerecord=f"{model_name}.hds",
        budget_filerecord=f"{model_name}.cbc",
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )

    # Write the simulation files
    sim.write_simulation()

    print(f"Model created in {model_ws}")

    # Run the simulation
    success, buff = sim.run_simulation()

    if success:
        print("Model run successfully")
        # Plot the results
        head = gwf.output.head().get_data()
        plt.figure(figsize=(8, 8))
        plt.imshow(head[0, :, :], cmap='viridis')
        plt.colorbar(label='Head')
        plt.title('Simulated Head')
        plt.xlabel('Column')
        plt.ylabel('Row')
        plt.savefig(os.path.join(model_ws, 'head_plot.png'))
        plt.close()
        print(f"Head plot saved in {model_ws}")
    else:
        print("Model run failed")

if __name__ == "__main__":
    create_simple_model()
