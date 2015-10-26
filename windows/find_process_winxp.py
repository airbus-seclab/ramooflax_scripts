#!/usr/bin/env python
#
# We are looking for "argv[1]" running under windows xp
#
# We install a filter on cr3 writes
# On each write, the vmm gives us control
# before the write operation
#
import sys

from ramooflax.core  import VM, CPUFamily, log
from ramooflax.utils import OSFactory, OSAffinity

# create logging for this script
log.setup(info=True, fail=True)

if len(sys.argv) < 2:
    log("fail", "gimme prog name")
    sys.exit(-1)

# Target process
process_name = sys.argv[1]

# Some offsets for Windows XP Pro SP3 EN 32 bits
settings = {"kprcb":0x20, "kthread":4,
            "eprocess":0x220, "name":0x174,
            "cr3":0x18, "next":0x88}

os = OSFactory(OSAffinity.WinXP, settings)
hook = os.find_process_filter(process_name)

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.attach()
vm.stop()
vm.cpu.filter_write_cr(3, hook)

while not vm.resume():
    continue

vm.cpu.release_write_cr(3)
log("info", "success: %#x" % os.get_process_cr3())
vm.detach()
