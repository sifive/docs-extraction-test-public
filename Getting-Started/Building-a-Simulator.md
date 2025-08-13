(building-a-simulator)=

# Building a Simulator

Here we outline the process for building your own Primo FPGA images, using Lion
as an example. This takes a while, so we have provided some pre-compiled images with FireSim -- you may skip
this section and proceed with {ref}`running-a-simulation` if you wish.

(building-a-simulator-prereqs)=

## Prerequisites

See {ref}`optional-build-prereqs`.  For now this can be skipped by sourcing:

```
. /nfs/teams/pe/share/firesim/aws-s3-env.sh
```

Then, initialize Federation as you would normally on a SiFive interactive machine of your choice:

```console
$ mkdir -p /scratch/$USER
$ cd /scratch/$USER
$ git clone --dissociate --reference-if-able /sifive/github-cache/federation.git git@github.com:sifive/federation
$ cd federation
$ ./scripts/quick-submodule-update
```

## Pre-synthesis RTL Simulation (Metasimulation)

Often before committing to building an FPGA image, it is wise to simulate the FireSim RTL for the target design in VCS or Verilator. We call this process
`metasimulation` as it simulates the simulator's (FireSim's) RTL. To launch a metasimulation of Leopard under VCS, run:

```{literalinclude} ../modified-frontend-examples.sh
:language: bash
:start-after: 'DOCREF START: frontend with metasim'
:end-before: 'DOCREF END: frontend with metasim'
```

This command will:

- Call EnterpriseGenerator to elaborate FIRRTL for the target design (Leopard)
- Run rhodium to compile the design, implement debug features, and link it with a FireSim simulation harness
- Compile the rhodium verilog to a VCS simulator (a metasimulator)
- Run a bare-metal binary on the metasimulator

This should approximately 30 minutes. Outputs from the metasimulation, including stdout and stderr (and waves if enabled), will be
found in `build/firesim/MetasimulationExecute/Default`. Inspecting the stderr (`sim.err`) should reveal something like:

```{code-block} console
:class: no-copybutton

C                   0:       3631 [1] pc=[000000008000003c] W[r30=000000008000103c][1] R[r 0=0000000000000000] R[r 0=0000000000000000] inst=[00001f17] DASM(00001f17)
C                   0:       3631 [1] pc=[0000000080000040] W[r 0=0000000000000000][0] R[r30=000000008000103c] R[r 3=000000000000053f] inst=[fc3f2223] DASM(fc3f2223)
C                   0:       3631 [1] pc=[0000000080000044] W[r 0=0000000000000000][0] R[r 0=0000000000000000] R[r 0=0000000000000000] inst=[ff9ff06f] DASM(ff9ff06f)
Termination Bridge detected exit on cycle 1864 with message:
All tests have succeeded

Simulation complete.
*** PASSED *** after 3736 cycles

Emulation Performance Summary
------------------------------
Wallclock Time Elapsed: 1.2 s
Host Frequency: 3.216 KHz
Target Cycles Emulated: 3736
Effective Target Frequency: 3.160 KHz
FMR: 1.02
Note: The latter three figures are based on the fastest target clock.
```

If we were to run the same bare metal binary on an
FPGA build of the same target, we should get the same reported cycle count
("Target Cycles Emulated"), just with considerably faster simulator performance
(MHz not KHz). Moreover, if we were to synthesize the Mallard's commit log printf using {ref}`Printf-Synthesis`, the
the Chisel `printf` output should match too. Speaking of which, lets build an FPGA image.

## Running an Example Build

To run an FPGA build of Leopard for Primo, re-use the same plan and select the publish step via the `--step PublishHamArtifact/Primo` flag:

```console
$ ./scripts/runWake build plan_leopard.json --step PublishHamArtifact/Primo
```

This will take approximately 12h to run, and will print a `HWDB entry`, a json fragment describing the built design, to stdout. It should look something like:

```{code-block} console
:class: no-copybutton

Skipping JFrog upload...

{
  "platform": "Primo",
  "fpga_image": {
    "bitstream": "build/firesim/CompilePrimoCheckpoint/Default/Default/run/redcomp.out/redcomp.outputs.tar.gz",
    "tool_version": "2022.12.2_2",
    "fpga_count": 1
  },
  "driver_tar": "build/firesim/CompileDriver/Default/driver-bundle.tar.gz",
  "simulator_spec": "build/firesim/RhodiumGenerateShim/Default/generated/FireSim-generated.simulator_spec.json",
  "dts": "build/firesim/DevicetreeExporter/FireSim/elaborated-target-design.dts"
}

All requested steps completed successfully.
Pass Unit
```

Your build may have slightly different fields if using a newer version of federation -- see {ref}`config-hwdb` for an up-to-date specification.
Note this build was not actually published to Artifactory or S3: this is made
plain by the local file paths in `build/`. To
actually publish the build, provide your AWS and JFROG credentials as environment variables, and then apply the `upload-hwdb`
overlay to the previous command like so:

```console
$ source /nfs/teams/pe/share/firesim/aws-s3-env.sh
$ wake build plan_leopard.json --step PublishHamArtifact/Primo
```

Assuming you have not altered a critical source file, Wake should be determine that it only needs to rerun the publish step and quickly produce something like the following:

```{code-block} console
:class: no-copybutton

16:18:22 [Info] [Thread 2] Uploading artifact: build/serengeti_1lion/PublishHamArtifact/Default/firesim_artifacts_3263439970

{
  "platform": "Primo",
  "fpga_image": {
    "bitstream": "s3://firesim-built-hardware-artifacts/7de961c7002012cbf074f9ccff54cfbc1c006111/6050772036/redcomp.outputs.tar.gz",
    "tool_version": "2022.12.2_2",
    "fpga_count": 1
  },
  "driver_tar": "s3://firesim-built-hardware-artifacts/7de961c7002012cbf074f9ccff54cfbc1c006111/6050772036/driver-bundle.tar.gz",
  "simulator_spec": "s3://firesim-built-hardware-artifacts/7de961c7002012cbf074f9ccff54cfbc1c006111/6050772036/simulator_spec.json",
  "dts": "s3://firesim-built-hardware-artifacts/7de961c7002012cbf074f9ccff54cfbc1c006111/6050772036/elaborated-target-design.dts"
}

All requested steps completed successfully.
Pass Unit
```

This time, note the S3 URIs (prefixed with `s3://`) indicating that this build should
be retrievable from any location with access to that S3 bucket. Additionally,
note the two hash-like strings in each URI -- the first corresponds to the federation SHA
used to do the build, the second is a content-specific hash, to ensure no two
builds using the same federation revision collide.

## Finding Prebuilt FPGA Images

To search all of the available FPGA images, use the {ref}`query-jfrog-artifacts` tool.
