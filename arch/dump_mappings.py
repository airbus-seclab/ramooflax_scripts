#!/usr/bin/env python
#
# Some address space handling code
#
#
import sys

from ramooflax import VM, CPUFamily, AddrSpace, PgMsk, log, disassemble

from amoco.arch.x86 import cpu_x86 as am
from amoco.cas.mapper import mapper as amapper

def disasm_wrapper(addr, data):
    return am.disassemble(data, address=addr)

def sstep_disasm(vm):
    insns = disassemble(vm, disasm_wrapper, vm.cpu.code_location())
    print insns.split('\n')[0]
    return True

def toto(vm):
    for a in vm.ads:
        pg = get_page(vm.ads[a], 0x80114e0)
        if pg is None:
            continue

        vm.cpu.set_active_cr3(a)
        bytes = vm.mem.vread(0x80114e0, 30)
        print "cr3 = 0x%x | %s " % (a, bytes.encode("hex"))

    vm.cpu.del_active_cr3()

def show_page(ads, vaddr):
    """
    Show page mapping for given virtual address
    """
    pgd_idx = vaddr>>22
    ptb_idx = vaddr>>12 & 0x3ff
    pgd = ads.pgd
    ptb = pgd[pgd_idx]
    if ptb is not None:
        pg = ptb[ptb_idx]
    else:
        pg = None
    log("info", "%s" % pg)

def get_page(ads, vaddr):
    pgd_idx = vaddr>>22
    ptb_idx = vaddr>>12 & 0x3ff
    pgd = ads.pgd
    ptb = pgd[pgd_idx]
    if ptb is not None:
        pg = ptb[ptb_idx]
    else:
        pg = None
    return pg

def search_page(page, data):
    blob = vm.mem.pread(page.paddr, 4<<10)
    idx = blob.find(data)
    if idx == -1:
        return None
    log("info", "found data @ paddr 0x%x" % (page.paddr+idx))
    return page.paddr+idx

def search_mem(ads, data):
    """
    Search user data into given address space
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

    if len(lst) != 0:
        for a in lst:
            log("info", "candidate 0x%x" % a)

    return lst


#############################
## write cr3 event handler ##
#############################
def on_write_cr3(vm):
    cr3 = vm.cpu.sr.cr3 & PgMsk.addr
    if not vm.ads.has_key(cr3):
        vm.ads[cr3] = AddrSpace(vm, cr3)
        log("info", "added new cr3 0x%x to ads (%d)" % (cr3, len(vm.ads)))
        #return True

    return False

################
##### MAIN #####
################
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

log.setup(info=True, fail=True, gdb=False, vm=True, ads=False)

vm.attach()
vm.stop()

vm.ads = {}
paging = vm.cpu.sr.cr0 & (1<<31)
if not paging or vm.cpu.mode != 32:
    log("fail", "bad mode (pg: %d, mode %d)" % (paging,vm.cpu.mode))
    sys.exit(-1)

vm.cpu.breakpoints.filter(None, sstep_disasm)
vm.cpu.filter_write_cr(3, on_write_cr3)
vm.interact2(dict(globals(), **locals()))
