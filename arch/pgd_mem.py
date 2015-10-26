#!/usr/bin/env python
#
# Collect address spaces throught write to cr3
# then look up for mapping of paging structures
# (pgd/ptb) inside them.
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
        log("info", "added new cr3 0x%x to ads (%d)" % (cr3, len(vm.ads)))
        search_ads(ads)

    return False

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

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.ads = {}

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          brk=True,  evt=False,
          sads=(True,log.green))

vm.attach()
vm.stop()

vm.cpu.filter_write_cr(3, wcr3)

log("info", "ready!")
vm.interact2(dict(globals(), **locals()))
