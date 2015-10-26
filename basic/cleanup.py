#!/usr/bin/env python
#
# Clean up vmm debugging session (if remaining cr3 tracking)
#
from ramooflax.core import VM, CPUFamily

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.attach()
vm.stop()
vm.cpu.del_active_cr3()
vm.detach()
