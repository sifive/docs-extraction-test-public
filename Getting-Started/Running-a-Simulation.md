(running-a-simulation)=

# Running a Simulation on Primo

## Configuring Input Files

FireSim executions are governed by three different configuration files:

1. A {ref}`config-runtime`, a json or yaml file that defines the execution, and refers to a HWDB entry and workload.
2. A {ref}`config-hwdb`, a json or json5 file which contains a single built FireSim simulator.
3. A {ref}`workload`, a json file which describes a set of RISC-V applications.

In this guide, we will explain only the parts of these files necessary for our purposes. You can find full descriptions of
all of the parameters in the {ref}`config-runtime` section.

Let's first look at `config_hwdb.json5`:

```{literalinclude} ../../../tools/firesim/manager/src/firesim/config/sample-backup-configs/sample_config_hwdb.json5
:language: json
```

This contains a verified prebuilt leopard image, which we'll use for this demo.
If you built an image in the previous tutorial, feel free to override this file with your own.

Next, have a look at the `config_runtime.yaml`:

```{literalinclude} ../../../tools/firesim/manager/src/firesim/config/sample-backup-configs/sample_config_runtime.yaml
:language: yaml
```

This file describes the runtime configuration for a single simulation. It calls out a workload, and uses the image in the `config_hwdb.json5` by default -- these can be overridden using
dedicated frontend arguments or by changing the settings in these files.

Finally, to boot Linux we need an image. FireSim Linux images consist of a
`bootbinary`
(generally, OpenSBI), and a rootfs image. These are defined in a
`workload.json` file, and called out with the `workload_name` key in the `config_runtime`. Workloads can be used
to define experiments with many simulations (e.g., SPEC2017), but in this
example it enumerates a single linux boot:

```{literalinclude} ../../../tools/firesim/manager/src/firesim/config/workloads/fsfl-demo.json
:language: json
```

Workload files are described in great detail in {ref}`workload-file` section, but note that the rootfs and
boot binary are specified with AWS S3 URIs to a published build in the cloud.

## Running the Simulation

By default, FireSim executions are run in Batch mode. Here, the specified workload, HWDB entry, and `config_runtime` settings are run without human input.
In batch mode each instance of the `FireSimExecute` step represents a single
end-to-end simulation, meaning if you are looking to hack on things in situ
{ref}`interactive-mode` may be a better choice (we'll cover that in the next section).
After the simulation has finished, the results are copied back to the
interactive machine you are running on into the
`build/<flow_name>/FireSimExecute/<tag_name>` directory and a tail of the
simulation stdout and stderr are printed.

To run a basic linux boot using the example files above, generate a execution-only wake build plan using:


```{literalinclude} ../../../continuous-integration/pre-merge/firesim-dev-tests/execute-test-primo
:language: bash
:end-before: 'DOCREF END: configure'
:start-after: 'DOCREF START: configure'
```

To configure the `FireSimExecute` step to run on a specific Slurm partition, use the `--execute-slurm-partition` argument. For this example we use the `dev` partition, but in general you should use the partition that corresponds to your team/use case. For details on the available partitions and their intended uses, see the [partitioning document](https://docs.google.com/document/d/18PCf569TN7CVIQoiyy5bS2_9C1FU3_4mDv9gLPzKSyw/edit?tab=t.0#heading=h.9ol31b7pqohp).

Then run the plan using:

```console
$ ./scripts/runWake build plan-execute-demo.json --step FireSimExecute/Primo
```

This will take about 15m, depending on Slurm queuing delays. After a minute or so, a path to the `fire-watcher` executable will be printed:

```{code-block} console
:class: no-copybutton

Running build graph steps for flow 'firesim':
  FireSimExecute (target goal): 1
    Primo

See 'build/firesim/flow.json' for the settings to be used, and 'build/firesim/flow.svg' for the rendered graph of dependencies.
Installed the firesim execution monitor. To get a running status of your simulations in a separate shell run:

./build/scripts/fire-watcher
```

In another shell (but from the same federation clone) running the `fire-watcher` script will show the status of the simulation, as well as other information about the execution. For example:

```{code-block} console
:class: no-copybutton

$ ./build/scripts/fire-watcher --tail-stdout 10

FireSim Execution Status @ 2025-01-31 23:02:14.874217+00:00
--------------------------------------------------------------------------------
Simulation execution directory:
/scratch/tmp/wake_rhorvath_pe03_scratch_6494796665
This status will update every 10s.
--------------------------------------------------------------------------------
Simulations
--------------------------------------------------------------------------------
Hostname: caq-kd39-cm11 | Job (Tag): Primo | Status: Initializing
--------------------------------------------------------------------------------
Summary
--------------------------------------------------------------------------------
1/1 simulations are still running.
--------------------------------------------------------------------------------

```

When the simulation is running `--tail-stdout 10` will show the the last 10 lines
of the uartlog.

Finally when completed, the build directory should look something like:

```{code-block} console
:class: no-copybutton

build/
└── <flow_name>/
    └── FireSimExecute/
        └── <tag_name>/
            ├── results-workload/
            │    └── 2024-09-24--17-48-23-fusdk-p470-minimal-None/
            │        └── fusdk-p470-minimal0/
            │            ├── performance_summary.json
            │            ├── heartbeat.csv
            │            ├── sim-run.sh
            │            ├── uartlog
            │            └── ...
            └── logs/
                ├── 2024-09-24--17-45-08-managerinit-57K7D19H8OEAQ4CB.log
                ├── 2024-09-24--17-45-08-infrasetup-3DQP03MCAJ67UBDH.log
                └── 2024-09-24--17-48-23-runworkload-FBTSVU28M3XJKGLL.log
```

With timestamps that correspond to your execution. The most critical result file is the *uartlog* log, which contains the combined stdout and stderr of the simulation. If you `tail` this file by running the following:

```console
$ find build -iname uartlog | xargs tail
```

You should see something like:

```{code-block} console
:class: no-copybutton

[    3.406340] systemd-shutdown[1]: All DM devices detached.
[    3.406780] systemd-shutdown[1]: All filesystems, swaps, loop devices, MD devices and DM devices detached.
[    3.409282] systemd-shutdown[1]: Syncing fileTermination Bridge detected exit on cycle 3690115101 with message:
All tests have succeeded

Simulation complete.
*** PASSED *** after 7380230210 cycles

Emulation Performance Summary
------------------------------
Wallclock Time Elapsed: 535.0 s
Host Frequency: 14.815 MHz
Target Cycles Emulated: 7380230210
Effective Target Frequency: 13.794 MHz
FMR: 1.07
Note: The latter three figures are based on the fastest target clock.

Script done on 2023-09-26 11:06:30-07:00
```

Note: the reported "Target Cycles Emulated" from your simulation should match the output above, alongside all of the
printf timestamps! However, wall clock time, effective target frequency, and FMR will
differ from run to run based on the load of the machine.

Congratulations on running your first FireSim simulation!
At this point, you can proceed with some of the more advanced tutorials, such as
using snapshotting, or rerun the instructions above with your own build from {ref}`Building-a-Simulator`.
