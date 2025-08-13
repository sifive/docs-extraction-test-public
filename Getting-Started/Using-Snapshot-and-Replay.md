(using-snapshot-and-replay)=

# Using Snapshot and Replay

Snapshot and replay is FireSim's mechanism for capturing **full-visibility** (registers, memories, combinational logic, assertions, and printfs) waveforms.

This proceeds in two phases.  First, during *snapshotting* on an FPGA:
  1. FireSim extracts the hardware state of the target, including all registers and memories in the input FIRRTL, some number of cycles before the point of interest ("state snapshotting").
  2. It than captures a complete I/O trace of the inputs that feed the FIRRTL up until the point of failure ("I/O tracing").
  3. Both the state snapshot and I/O trace are written to a snapshot file.
  4. This process is repeated continuously to save a user-specified rolling window of snapshots.

Then, during *replay*, snapshot files are passed to a VCS or Verilator simulator generated from the same input FIRRTL:
  1. Initial state of memories and registers are initialized with the snapshot-described state values.
  2. Input traces are fed to the DUT to replay the behavior seen on the FPGA but with full-visibility and with FireSim idle-cycles removed

## Snapshotting Walkthrough

Using Wake, both the steps above can be combined into a single build-graph execution.
This is convenient when one needs to reproduce a failure
seen on previous simulation (e.g., in CI) where no snapshots were collected. As before, clone federation and download the replay archive:

```console
$ mkdir -p /scratch/$USER
$ cd /scratch/$USER
$ git clone --dissociate --reference-if-able /sifive/github-cache/federation.git git@github.com:sifive/federation
$ cd federation
$ ./scripts/quick-submodule-update
$ source /nfs/teams/pe/share/firesim/aws-s3-env.sh
```

For this tutorial we're going to reuse the same instrumented leopard design as before:

```{literalinclude} ../../../tools/firesim/manager/src/firesim/config/sample-backup-configs/sample_config_hwdb.json5
:start-after: 'DOCREF START: Example HWDB Entry'
:end-before: 'DOCREF END: Example HWDB Entry'
:language: yaml
```

Note the presence of the `replay_archive`: this is a self-contained tarball of a VCS replay simulator. Checking for
this field in a HWDB is a quick-and-dirty way to check if a simulator has been built with snapshotting.

Now, invoke FireSim's build frontend as follows:

```{literalinclude} ../modified-frontend-examples.sh
:language: bash
:start-after: 'DOCREF START: frontend snapshot'
:end-before: 'DOCREF END: frontend snapshot'
```

This uses the same `config_runtime.yaml` as in the original demo, but mutates
the provided `config_runtime.yaml` to enable snapshotting:

* `--execute-max-cycles` forces the simulation to time out after the specified number of base cycles have elapsed so you don't have to wait for a complete linux boot to execute (which runs slower under snapshotting).
* `--execute-snapshot-start` enables snapshotting at base cycle 1.

Under the default window size of 100K cycles, this will produce 10 snapshot
files. These will be copied back and replayed in parallel, providing 10
full-visibility FSDBs for each interval of the execution.

That's a whirlwind tour of snapshot and replay! Combined with tools such
as {ref}`assertion-synthesis` (to determine _where_ to capture a snapshot),
snapshot-and-replay is an extremely productive tool for debugging broken target
designs.

## Out-of-Band Replay Walkthrough

To replay snapshot files out-of-band, we'll use the `ReplayExecute` step in Federation's wake build graph infrastructure. As before, setup a federation clone on a SiFive data-center
machine with access to Primo (e.g., `pe03`).
The specific revision should not matter because the replay simulator has already been built for you and is included in the HWDB.

```console
$ mkdir -p /scratch/$USER
$ cd /scratch/$USER
$ git clone --dissociate --reference-if-able /sifive/github-cache/federation.git git@github.com:sifive/federation
$ cd federation
$ ./scripts/quick-submodule-update
```

Now, invoke FireSim's frontend to generate a build plan for replay:

```console
$ ./scripts/runWake --in firesim_tester configure --hwdb-path <PATH-TO-HWDB> --replay-snapshot-files <PATH-TO-SNAPSHOT> ... <PATH-TO-SNAPSHOT-N>
```

To replay the snapshots run:

```console
$ ./scripts/runWake build plan.json --step ReplayExecute/FireSim
```

This will run a replay simulator for each provided snapshot, in parallel. This
way, larger waveforms (10s-100s millions of cycles) can be replayed without
radically increasing replay latency. When finished, you'll find results in: `./build/firesim/ReplayExecute/FireSim/<snapshot-file-name>`. So running:

```console
$ ls ./build/firesim/ReplayExecute/FireSim/snapshot.txt0/
```

Should produce:

```{code-block} console
:class: no-copybutton

sim.err  sim.out  snapshot.txt0.fsdb  ucli.key
```

`snapshot.txt0.fsdb` should contain a full-visibility (all registers, memories,
and combinational paths, subject to CIRCT optimizations) replay of what occurred
on the FPGA.  `sim.err` should contain the same chisel printfs of the commit
trace you'd get by running an RTL simulation. Feel free to open up the FSDB and
inspect the waves. For those feeling especially ambitious, try running a
metasimulation and confirm the results (e.g., the commit log printfs) are the
same.
