#!/usr/bin/env python

import sys
import struct

from collections    import defaultdict
from ramooflax      import VM, CPUFamily, log
from ramooflax      import AddrSpace, PgMsk, Page, PageTable

def wcr3(vm):
    cr3 = vm.cpu.sr.cr3 & PgMsk.addr
    if not cr3:
        return False

    if not vm.ads.has_key(cr3) and cr3!= 0x36000:
        ads = AddrSpace(vm, cr3)
        vm.ads[cr3] = ads
        log("info", "added new cr3 0x%x to ads (%d)" % (cr3, len(vm.ads)))
    elif len(vm.ads) > 1:
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

################
##### MAIN #####
################
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.ads = {}

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          ads=False, brk=True,
          evt=False, fsm=(True,log.blue))

vm.attach()
vm.stop()

vm.cpu.filter_write_cr(3, wcr3)

log("info", "ready!")
vm.interact2(dict(globals(), **locals()))
