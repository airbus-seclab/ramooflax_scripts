#!/usr/bin/env python
#
# Collect some address spaces throught write to cr3
# once "nr_cr3" have been collected, look up for
# kernel memory pages with user mappings.
#
from collections     import defaultdict
from ramooflax.core  import VM, CPUFamily, log
from ramooflax.utils import AddrSpace, PgMsk

def wcr3(vm):
    cr3 = vm.cpu.sr.cr3 & PgMsk.addr
    if not cr3:
        return False

    if not vm.ads.has_key(cr3):
        ads = AddrSpace(vm, cr3)
        vm.ads[cr3] = ads
        for p in ads.iter_pages(user=False):
            vm.kppg[p.paddr].append((cr3,p))
        log("info", "added new cr3 0x%x to ads (%d)" % (cr3, len(vm.ads)))

    return False

# Detect any kernel physical page which might be
# mapped elsewhere as user one(s) into currently known
# address spaces (vm.ads)
def find_kmem(vm):
    log("fkm", "Looking for kernel pages into user mappings")

    #check if they have another mapping with user privilege
    fmt = "U ads 0x%x match K ads 0x%x:\n (user) %s\n (krnl) %s"
    for klst in vm.kppg.itervalues():
        for ka,kp in klst:
            for a in vm.ads:
                ulst = vm.ads[a].search_paddr(kp.paddr,user=True)
                if len(ulst) != 0:
                    for p in ulst:
                        log("fkm", fmt % (a,ka,p,kp))

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.nr_cr3 = 1
vm.ads = {}
#keep track of every kernel physical pages
vm.kppg = defaultdict(list)

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          brk=True,  evt=False,
          fkm=(True,log.blue))

vm.attach()
vm.stop()

vm.cpu.filter_write_cr(3, wcr3)

log("info", "ready!")
while len(vm.ads) < vm.nr_cr3:
    vm.resume()

vm.detach()
find_kmem(vm)
