#!/usr/bin/env python

from x86_desc  import *
from ramooflax import VM, CPUFamily, log, PgMsk

def kernel_stack(vm):
    sp0 = vm.mem.read_dword(vm.cpu.sr.tr_base+4)
    ss3 = vm.mem.read_dword(sp0 - 4)
    sp3 = vm.mem.read_dword(sp0 - 8)

    addr = vm.cpu.sr.gdtr_base + (ss3 & (~3))
    desc = SegmentDescriptor(vm.mem.vread(addr, 8))
    if desc.dpl != 3:
        return False

    sp3 = vm.cpu.linear(desc.base, sp3)

    nm_sz = 100
    stack = (sp3 & PgMsk.addr) + 4096
    while True:
        try:
            vm.mem.translate(stack)
        except:
            break
        stack += 4096

    nm_addr = stack - nm_sz
    name = vm.mem.vread(nm_addr, nm_sz).strip('\x00').split('\x00')[-1]
    log("info", "[%s]" % (repr(name)))
    return False

#
# Main
#
peer = "172.16.131.128:1337"
vm = VM(CPUFamily.Intel, peer)

vm.ads = {}

log.setup(info=True, fail=True,
          gdb=False, vm=True,
          ads=False, brk=False, evt=False)

vm.attach()
vm.stop()

vm.cpu.breakpoints.add_data_w(vm.cpu.sr.tr_base+4, 4, kernel_stack)

log("info", "ramooflax ready!")
vm.interact2(dict(globals(), **locals()))
