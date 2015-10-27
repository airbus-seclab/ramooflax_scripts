#!/usr/bin/env python
#
# Filter on CPUID=4
#
from ramooflax.core  import VM, CPUFamily, log

def cpuid_hook(vm):
    log("info", "cpuid(1) = 0x%x 0x%x 0x%x 0x%x" % \
            (vm.cpu.gpr.eax,vm.cpu.gpr.ebx,vm.cpu.gpr.ecx,vm.cpu.gpr.edx))
    return False

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True)

vm.attach()
vm.stop()

vm.cpu.filter_cpuid(cpuid_hook, 1)

log("info", "ramooflax ready!")
vm.interact2(dict(globals(), **locals()))
