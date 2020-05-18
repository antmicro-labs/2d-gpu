#!/usr/bin/env python3

# This file is Copyright (c) 2015-2019 Florent Kermarrec <florent@enjoy-digital.fr>
# License: BSD

import argparse

from migen import *

from litex.boards.platforms import arty
from litex.build.xilinx.vivado import vivado_build_args, vivado_build_argdict

from litex.soc.cores.clock import *
from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

#------ Our includes
from litex.soc.cores.gpio import *
from litex.boards.platforms.arty import *
#------

from litedram.modules import MT41K128M16
from litedram.phy import s7ddrphy

from liteeth.phy.mii import LiteEthPHYMII


# CRG ----------------------------------------------------------------------------------------------

class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys       = ClockDomain()
        self.clock_domains.cd_sys2x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x     = ClockDomain(reset_less=True)
        self.clock_domains.cd_sys4x_dqs = ClockDomain(reset_less=True)
        self.clock_domains.cd_clk200    = ClockDomain()
        self.clock_domains.cd_eth       = ClockDomain()

        # # #

        self.submodules.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(~platform.request("cpu_reset"))
        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys,       sys_clk_freq)
        pll.create_clkout(self.cd_sys2x,     2*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x,     4*sys_clk_freq)
        pll.create_clkout(self.cd_sys4x_dqs, 4*sys_clk_freq, phase=90)
        pll.create_clkout(self.cd_clk200,    200e6)
        pll.create_clkout(self.cd_eth,       25e6)

        self.submodules.idelayctrl = S7IDELAYCTRL(self.cd_clk200)

        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)

# BaseSoC ------------------------------------------------------------------------------------------

class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(100e6), with_ethernet=False, with_etherbone=False, **kwargs):
        platform = arty.Platform()

        # SoCCore ----------------------------------------------------------------------------------
        SoCCore.__init__(self, platform, clk_freq=sys_clk_freq, **kwargs)

        # CRG --------------------------------------------------------------------------------------
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # DDR3 SDRAM -------------------------------------------------------------------------------
        if not self.integrated_main_ram_size:
            self.submodules.ddrphy = s7ddrphy.A7DDRPHY(platform.request("ddram"),
                memtype        = "DDR3",
                nphases        = 4,
                sys_clk_freq   = sys_clk_freq,
                interface_type = "MEMORY")
            self.add_csr("ddrphy")
            self.add_sdram("sdram",
                phy                     = self.ddrphy,
                module                  = MT41K128M16(sys_clk_freq, "1:4"),
                origin                  = self.mem_map["main_ram"],
                size                    = kwargs.get("max_sdram_size", 0x40000000),
                l2_cache_size           = kwargs.get("l2_size", 8192),
                l2_cache_min_data_width = kwargs.get("min_l2_data_width", 128),
                l2_cache_reverse        = True
            )

        # Ethernet ---------------------------------------------------------------------------------
        if with_ethernet:
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            self.add_ethernet(phy=self.ethphy)

        # Etherbone --------------------------------------------------------------------------------
        if with_etherbone:
            self.submodules.ethphy = LiteEthPHYMII(
                clock_pads = self.platform.request("eth_clocks"),
                pads       = self.platform.request("eth"))
            self.add_csr("ethphy")
            self.add_etherbone(phy=self.ethphy)

#------- GPIO module
        ckio_pins=[
            ("ckio", 0, Pins("ck_io:ck_io0"), IOStandard("LVCMOS33")),
            ("ckio", 1, Pins("ck_io:ck_io1"), IOStandard("LVCMOS33")),
            ("ckio", 2, Pins("ck_io:ck_io2"), IOStandard("LVCMOS33")),
            ("ckio", 3, Pins("ck_io:ck_io3"), IOStandard("LVCMOS33")),
            ("ckio", 4, Pins("ck_io:ck_io4"), IOStandard("LVCMOS33")),
            ("ckio", 5, Pins("ck_io:ck_io5"), IOStandard("LVCMOS33")),
            ("ckio", 6, Pins("ck_io:ck_io6"), IOStandard("LVCMOS33")),
            ("ckio", 7, Pins("ck_io:ck_io7"), IOStandard("LVCMOS33")),
            ("ckio", 8, Pins("ck_io:ck_io8"), IOStandard("LVCMOS33")),
            ("ckio", 9, Pins("ck_io:ck_io9"), IOStandard("LVCMOS33")),
            ("ckio", 10, Pins("ck_io:ck_io10"), IOStandard("LVCMOS33")),
            ("ckio", 11, Pins("ck_io:ck_io11"), IOStandard("LVCMOS33")),
            ("ckio", 12, Pins("ck_io:ck_io12"), IOStandard("LVCMOS33")),
            ("ckio", 13, Pins("ck_io:ck_io13"), IOStandard("LVCMOS33")),
            ("ckio", 14, Pins("ck_io:ck_io14"), IOStandard("LVCMOS33")),
            ("ckio", 15, Pins("ck_io:ck_io15"), IOStandard("LVCMOS33")),
            ("ckio", 16, Pins("ck_io:ck_io16"), IOStandard("LVCMOS33")),
            ("ckio", 17, Pins("ck_io:ck_io17"), IOStandard("LVCMOS33")),
            ("ckio", 18, Pins("ck_io:ck_io18"), IOStandard("LVCMOS33")),
            ("ckio", 19, Pins("ck_io:ck_io19"), IOStandard("LVCMOS33")),
            ("ckio", 20, Pins("ck_io:ck_io20"), IOStandard("LVCMOS33")),
            ("ckio", 21, Pins("ck_io:ck_io21"), IOStandard("LVCMOS33")),
            ("ckio", 22, Pins("ck_io:ck_io22"), IOStandard("LVCMOS33")),
            ("ckio", 23, Pins("ck_io:ck_io23"), IOStandard("LVCMOS33")),
            ("ckio", 24, Pins("ck_io:ck_io24"), IOStandard("LVCMOS33")),
            ("ckio", 25, Pins("ck_io:ck_io25"), IOStandard("LVCMOS33")),
            ("ckio", 26, Pins("ck_io:ck_io26"), IOStandard("LVCMOS33")),
            ("ckio", 27, Pins("ck_io:ck_io27"), IOStandard("LVCMOS33")),
            ("ckio", 28, Pins("ck_io:ck_io28"), IOStandard("LVCMOS33")),
            ("ckio", 29, Pins("ck_io:ck_io29"), IOStandard("LVCMOS33")),
            ("ckio", 30, Pins("ck_io:ck_io30"), IOStandard("LVCMOS33")),
            ("ckio", 31, Pins("ck_io:ck_io31"), IOStandard("LVCMOS33")),
            ("ckio", 32, Pins("ck_io:ck_io32"), IOStandard("LVCMOS33")),
            ("ckio", 33, Pins("ck_io:ck_io33"), IOStandard("LVCMOS33")),
            ("ckio", 34, Pins("ck_io:ck_io34"), IOStandard("LVCMOS33")),
            ("ckio", 35, Pins("ck_io:ck_io35"), IOStandard("LVCMOS33")),
            ("ckio", 36, Pins("ck_io:ck_io36"), IOStandard("LVCMOS33")),
            ("ckio", 37, Pins("ck_io:ck_io37"), IOStandard("LVCMOS33")),
            ("ckio", 38, Pins("ck_io:ck_io38"), IOStandard("LVCMOS33")),
            ("ckio", 39, Pins("ck_io:ck_io39"), IOStandard("LVCMOS33")),
            ("ckio", 40, Pins("ck_io:ck_io40"), IOStandard("LVCMOS33")),
            ("ckio", 41, Pins("ck_io:ck_io41"), IOStandard("LVCMOS33"))
        ]
        self.platform.add_extension(ckio_pins)

        sig= self.platform.request("ckio")
        self.submodules.gpjajo= GPIOOut(sig)
        self.add_csr("gpjajo")

# Build --------------------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LiteX SoC on Arty")
    builder_args(parser)
    soc_sdram_args(parser)
    vivado_build_args(parser)
    parser.add_argument("--with-ethernet", action="store_true", help="enable Ethernet support")
    parser.add_argument("--with-etherbone", action="store_true", help="enable Etherbone support")
    args = parser.parse_args()

    assert not (args.with_ethernet and args.with_etherbone)
    soc = BaseSoC(with_ethernet=args.with_ethernet, with_etherbone=args.with_etherbone,
        **soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(**vivado_build_argdict(args))


if __name__ == "__main__":
    main()
