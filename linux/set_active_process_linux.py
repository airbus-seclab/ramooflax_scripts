#!/usr/bin/env python
#
# We are looking for "argv[1]" running under debian
#
# We install the Linux26.find_process_filter on cr3 writes
# The framework will call our filter Before each write
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

# Some offsets for debian 2.6.32-5-486 kernel
settings = {"thread_size":8192, "comm":540, "next":240, "mm":268, "pgd":36}
os = OSFactory(OSAffinity.Linux26, settings)
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
vm.cpu.set_active_cr3(os.get_process_cr3(), True, OSAffinity.Linux26)
log("info", "active cr3 installed for %#x" % os.get_process_cr3())
vm.detach()
