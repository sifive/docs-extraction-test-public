(prereqs)=

# Prerequisites

FireSim's use of FPGAs external to the SiFive datacenter requires some extra
setup. Before proceeding, please email compute@sifive.com ([mailto link](mailto:compute@sifive.com?subject=Request%20For%20FireSim%20Access))
with the following subject:

```
Request for FireSim Access
```

And body:

```
Hello,

In order to use FireSim, can I (<unixid>):
* have a home directory created in the Primo Colo
* have SubUID and SubGID ranges assigned in IPA
* be added to the siemensenv UNIX group.

Thanks,
```

Once your request has been fulfilled, register `salloc_copy`'s public key with the Primo cluster using the following command:

```console
$ ssh-copy-id -i ~/.ssh/id_rsa_salloc_copy $USER@caq-ki45-main2
```

This is required only because Primo NFS is not linked to SiFive SCL's NFS.  

## Testing your Credentials

After completing the setup {ref}`prereqs` run the following `wake` command in a Federation clone on your preferred SiFIve interactive machine (note: you cannot clone Federation on Primo systems):

```console
$ ./scripts/runWake -v -x 'testPrimoPodman Nil' --in firesim
```

If you have set your credentials correctly you should see the following output:

```{code-block} console
:class: no-copybutton

receiving incremental file list
.build/
.build/podman-result-28312.json

sent 47 bytes  received 443 bytes  980.00 bytes/sec
total size is 279  speedup is 0.57
receiving file list ... done
firesim/
firesim/deploy/
firesim/deploy/results-workload/
firesim/deploy/results-workload/dummy_output.txt

sent 110 bytes  received 203 bytes  626.00 bytes/sec
total size is 0  speedup is 0.00
OUTPUTS: firesim/deploy/results-workload/dummy_output.txt
testPrimoPodman Nil: Result Unit Error = Pass Unit
```

If not check the following:

1. Ensure you belong to the `siemensenv` UNIX group.
2. Ensure your public key (from the key-pair you use to SSH into SiFive's data center) has been registered with SiFive's IPA server. Login here <https://ipa01.internal.sifive.com/ipa/ui/> with your UNIX username and password. Note, only very tenured employees may need to do this.
3. Ensure you have a SubUID and SubGID allocated to you by clicking the `Subordinate ids` tab on the IPA server. There will be a row with a range of IDs that have been allocated for you which will look like:

```{figure} ipa_subuid_page.png
:align: center
:width: 800px

Subordinate IDs page on IPA server

```

If any of the following are not true, post a follow up in your original compute ticket. If you're still stuck contact the {xref}`firesim-slack` with the output of the script.

(optional-build-prereqs)=

## Optional Build Prerequisites

In order to publish your builds and annotate them as belonging to you, you'll need to:

1. Sign into Artifactory from Okta and [generate an Identity Token.](https://jfrog.com/help/r/platform-api-key-deprecation-and-the-new-reference-tokens/how-to-get-an-identity-token-in-3-steps)

2. Then, in any shell in which you wish to publish a build, source:

```
. /nfs/teams/pe/share/firesim/aws-s3-env.sh
```

3. Finally, override the `FIRESIM_JFROG_API_KEY` environment variable with your own key:

```
export FIRESIM_JFROG_API_KEY=<your key>
```


