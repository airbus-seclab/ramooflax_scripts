#!/usr/bin/env python

import sys
import struct

from collections    import defaultdict
from ramooflax      import VM, CPUFamily, log
from ramooflax      import AddrSpace, PgMsk, Page, PageTable

# Detect any kernel physical page which might be
# mapped elsewhere as user one(s) into currently known
# adress spaces (vm.ads)
def find_kmem(vm):
    log("fkm", "Looking for kernel pages into user mappings")
    #keep track of every kernel physical pages
    vm.kppg = defaultdict(list)
    for a in vm.ads:
        for p in vm.ads[a].iter_pages(user=False):
            vm.kppg[p.paddr].append((a,p))

    #check if they have another mapping with user privilege
    fmt = "U ads 0x%x match K ads 0x%x:\n (user) %s\n (krnl) %s"
    for klst in vm.kppg.itervalues():
        for ka,kp in klst:
            for a in vm.ads:
                ulst = vm.ads[a].search_paddr(kp.paddr,user=True)
                if len(ulst) != 0:
                    for p in ulst:
                        log("fkm", fmt % (a,ka,p,kp))


# For given address space,
# search mappings of each PGD/PTs
def search_ads(ads):
    log("sads", "Searching PGD/PTs mapping into address space 0x%x" % ads.pgd.addr)

    ptb_addrs = [ads.pgd.addr]
    for p in ads.iter_pagetables():
        ptb_addrs.append(p.addr)

    log("sads", "PGD/PTs : %s" % " ".join([hex(i) for i in ptb_addrs]))
    for a in ptb_addrs:
        plst = ads.search_paddr(a)
        if len(plst) != 0:
            log("sads", "match for 0x%x" % a)
            for p in plst:
                log("sads", "%s" % p)

def wcr3(vm):
    cr3 = vm.cpu.sr.cr3 & PgMsk.addr
    if not cr3:
        return False

    if not vm.ads.has_key(cr3):
        ads = AddrSpace(vm, cr3)
        vm.ads[cr3] = ads
        log("info", "added new cr3 0x%x to ads (%d)" % (cr3, len(vm.ads)))
        search_ads(ads)
    elif len(vm.ads) > 1:
        find_kmem(vm)

    return False



################
##### MAIN #####
################
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.ads = {}

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          ads=False, brk=True, evt=False,
          fkm=(True,log.blue), sads=(True,log.green))

vm.attach()
vm.stop()

vm.cpu.filter_write_cr(3, wcr3)

log("info", "ready!")
vm.interact2(dict(globals(), **locals()))
