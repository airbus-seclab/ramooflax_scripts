#!/usr/bin/env python
#
# Collect some address spaces throught write to cr3
# once "nr_cr3" have been collected, look up for
# shared memory pages between them.
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
    elif len(vm.ads) >= vm.nr_cr3:
        return find_shared(vm)

    return False

# Detect physical pages that might be shared
# accross different address spaces
def find_shared(vm):
    log("fsm", "Find shared pages accross address spaces")

    vm.all_pages = defaultdict(list)
    for a in vm.ads:
        for p in vm.ads[a].iter_pages(user=True):
            vm.all_pages[p.paddr].append((a,p))

    for addr,pages in vm.all_pages.iteritems():
        if len(pages) > 1:
            log("fsm", "match for 0x%x" % addr)
            for ads,pg in pages:
                log("fsm", "ads 0x%x: %s" % (ads,pg))

    return True

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.nr_cr3 = 5
vm.ads = {}

log.setup(info=True, fail=True, gdb=False,
          vm=True,   brk=True,  evt=False,
          fsm=(True,log.blue))

vm.attach()
vm.stop()

vm.cpu.filter_write_cr(3, wcr3)

log("info", "ready!")
vm.interact2(dict(globals(), **locals()))
