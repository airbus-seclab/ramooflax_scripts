#!/usr/bin/env python
#
# read msr 0x1b = APIC_BASE
#
from ramooflax.core  import VM, CPUFamily, log

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True)

vm.attach()
vm.stop()

vm.cpu.msr.read(0x1b)
log("info", "MSR(APIC_BASE) = 0x%x 0x%x" % (vm.cpu.msr.eax, vm.cpu.msr.edx))

vm.detach()
