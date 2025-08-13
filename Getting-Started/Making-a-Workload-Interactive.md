(making-a-workload-interactive)=

# Making your Workload Interactive

When deploying a {ref}`Workload<workload-file>` it is very useful interactively login and manipulate
the {ref}`target` machine and it's operating system. This interactive mode is most useful when debugging a workload
or just starting to become familiar with FireSim. Note: this mode ruins the repeatability of the simulation.

To modify your existing workload to utilize this specialized rootfs, add the following lines to your `workload.json`:

```
"modify_rootfs_script": "workloads/scripts/modify_rootfs_interactive.sh",
```

To learn more about how this works, see {ref}`specializing-rootfs`.

(running-in-interactive-mode)=

## Running in Interactive Mode

Using the build plan from the previous section {ref}`running-a-simulation`, enable interactive mode by setting the `Interactive` setting to `true` in the `FireSimExecute` step (or by re-running the frontend with the `--execute-interactive` flag). You also likely want to disable auto termination by setting `terminate_on_completion` to `false` in the `FireSimExecute` step settings as well. This is done for you automatically when using the frontend.

Then run:

```console
$ ./scripts/runWake build plan-execute-demo.json --step FireSimExecute/Primo
```

With `Interactive` set to `true`, the `FireSimExecute` step will setup the manager and leave the container idle on the remote machine until you connect to it. To find the hostname, execution directory, and other information on the running container use `fire-watcher`. Then, to connect to the container run the following commands:

```console
$ ssh <ALLOCATED HOSTNAME>
$ cd <EXECUTION DIRECTORY FROM fire-watcher>
$ ./attach-to-container.sh
```

## Interacting with the Simulation

After you attach to the container in interactive mode using the instructions in {ref}`running-in-interactive-mode`, you will need to program the FPGA and start the simulation using the commands:

```console
$ firesim infrasetup
$ firesim runworkload &
```

Once the simulation is running, you can attach to it using:

```console
$ screen -r fsim0
```

This will drop you into the booting (or already booted) simulation. You may need to wait a few minutes for boot to complete, but now you can login to the system! The username is `root` and the password is
`sifive`. At this point, you should be presented with a regular console,
where you can type commands into the simulation and run programs. For example:

```{code-block} console
:class: no-copybutton

FreedomUSDK private Panda-codebase-FUSDK-public-2022.10.00 firesim-lion hvc0

firesim-lion login: root
Password:
[    4.180747] login[181]: pam_unix(login:session): session opened for user root(uid=0) by LOGIN(uid=0)
[    4.185181] systemd[1]: Starting User Database Manager...
[    4.229714] systemd[1]: Started User Database Manager.
[    4.252919] systemd[1]: Created slice User Slice of UID 0.
[    4.255939] systemd[1]: Starting User Runtime Directory /run/user/0...
[    4.266870] systemd-logind[176]: New session c1 of user root.
[    4.273338] systemd[1]: Finished User Runtime Directory /run/user/0.
[    4.275037] systemd[1]: Starting User Manager for UID 0...
[    4.282194] systemd[189]: pam_warn(systemd-user:setcred): function=[pam_sm_setcred] flags=0x8002 service=[systemd-user] terminal=[<unknown>] user=[root] ruser=[<unknown>] rhost=[<unknown>]
[    4.629693] systemd[189]: Queued start job for default target Main User Target.
[    4.631760] systemd[189]: Created slice User Application Slice.
[    4.631977] systemd[189]: Reached target Paths.
[    4.632166] systemd[189]: Reached target Timers.
[    4.633124] systemd[189]: Starting D-Bus User Message Bus Socket...
[    4.643952] systemd[189]: Listening on D-Bus User Message Bus Socket.
[    4.644224] systemd[189]: Reached target Sockets.
[    4.644414] systemd[189]: Reached target Basic System.
[    4.649902] systemd[1]: Started User Manager for UID 0.
[    4.650053] systemd[1]: Started Session c1 of User root.
[    4.650694] systemd[189]: Reached target Main User Target.
[    4.651088] systemd[189]: Startup finished in 361ms.
[    4.664355] login[195]: ROOT LOGIN  on '/dev/hvc0'
root@firesim-lion:~# uname -a
Linux firesim-lion 5.19.7 #1 SMP Wed Jan 1 00:00:00 UTC 2020 riscv64 GNU/Linux
```

At this point, you can run workloads as you'd like. To finish off this tutorial,
let's power off the simulated system and see what the manager does. To do so,
in the console of the simulated system, run `poweroff -f`:

```{code-block} console
:class: no-copybutton

root@firesim-lion:~# poweroff -f
Powering off.
[    5.457230] kvm: exiting hardware virtualization
[Termination Bridge detected exit on cycle 5737692582 with message:
All tests have succeeded

[screen is terminating]
```

At this point you're free to re-flash the FPGA and run the manager commands above, if you wish. To flash the FPGA without having to repeat URI downloading, you can use the following command instead of `infrasetup`:
```console
$ firesim flashfpga
```
Note that if you make any changes to the rootfs during the interactive session, you should default to `infrasetup` to ensure reproducibility.
Otherwise, if you're finished with your simulation just hit `control+C` on the terminal that is running the wake job and your container will be pulled down and the results of your simulation(s) copied back as if it were batch mode.
This may take a few seconds as we need to make sure any FPGA reservations are removed and the driver process is terminated before copying any files.

In general, this mode should be used to debug and finalize any workload you would like to run in a batch mode.
To customize the workload, in a deterministic and repeatable way, see {ref}`specializing-rootfs`
