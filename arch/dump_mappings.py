#!/usr/bin/env python
#
# Collect address spaces through write to
# cr3 into 'vm.ads' dictionnary. The keys
# are the cr3 values.
#
# You can get interactive 'ctrl+c' and
# play with them.
#
# This script provides you with example
# functions "search_mem" that will only
# search into virtual memory of the given
# address space
#
# >>> [hex(a) for a in vm.ads]
# ['0x35e02000', '0x35c63000', '0x3624d000', '0x35cc8000']
#
# >>> search_mem(vm.ads[0x35c63000], "ELF")
# found data @ paddr 0x3ef1d001
# found data @ paddr 0x3fdc7001
# found data @ paddr 0x36822001
# found data @ paddr 0x3ffe2501
# found data @ paddr 0x3ffe1f60
# [1056034817, 1071411201, 914497537, 1073620225, 1073618784]
#

import sys

from ramooflax.core  import VM, CPUFamily, log
from ramooflax.utils import AddrSpace, PgMsk

def get_page(ads, vaddr):
    """
    Simple get physical page for 'vaddr' into address space 'ads'
    """
    pgd_idx = vaddr>>22
    ptb_idx = vaddr>>12 & 0x3ff
    pgd = ads.pgd
    ptb = pgd[pgd_idx]
    if ptb is not None:
        pg = ptb[ptb_idx]
    else:
        pg = None
    return pg

def show_page(ads, vaddr):
    pg = get_page(ads, vaddr)
    log("info", "%s" % pg)

def search_page(page, data):
    blob = vm.mem.pread(page.paddr, 4<<10)
    idx = blob.find(data)
    if idx == -1:
        return None

    log("info", "found data @ paddr 0x%x" % (page.paddr+idx))
    return page.paddr+idx

def search_mem(ads, data):
    """
    Search user data into given address space 'ads'
    """
    lst = []

    for pde in ads.pgd.pde:
        if not pde.p:
            continue
        if pde.large:
            if pde.page.mode == "user":
                addr = search_page(pde.page, data)
                if addr is not None:
                    lst.append(addr)
        else:
            ptb = pde.ptb
            for pte in ptb.pte:
                if pte.p and pte.page.mode == "user":
                    addr = search_page(pte.page, data)
                    if addr is not None:
                        lst.append(addr)
    return lst

def on_write_cr3(vm):
    cr3 = vm.cpu.sr.cr3 & PgMsk.addr
    if not vm.ads.has_key(cr3):
        vm.ads[cr3] = AddrSpace(vm, cr3)
        log("info", "added new cr3 0x%x to ads (#%d)" % (cr3, len(vm.ads)))
        #return True

    return False

##
## Main
##
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True, gdb=False, vm=True)

vm.attach()
vm.stop()

vm.ads = {}
vm.cpu.filter_write_cr(3, on_write_cr3)

vm.interact2(dict(globals(), **locals()))
