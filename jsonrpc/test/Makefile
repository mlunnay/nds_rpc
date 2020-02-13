#---------------------------------------------------------------------------------
.SILENT:
.SUFFIXES:
#---------------------------------------------------------------------------------
ifeq ($(strip $(DEVKITARM)),)
$(error "Please set DEVKITARM in your environment. export DEVKITARM=<path to>devkitARM)
endif

include $(DEVKITARM)/ds_rules

export TARGET		:=	dswifitest
export TOPDIR		:=	$(CURDIR)

TEXT1 		:= jsonrpc_example
TEXT2 		:= Michael Lunnay
TEXT3 		:= 

ICON 		:= -b $(CURDIR)/data/logo.bmp

#---------------------------------------------------------------------------------
# path to tools - this can be deleted if you set the path in windows
#---------------------------------------------------------------------------------
export PATH		:=	$(DEVKITARM)/bin:$(PATH)

.PHONY: $(TARGET).arm7 $(TARGET).arm9

#---------------------------------------------------------------------------------
# main targets
#---------------------------------------------------------------------------------
#I don't want .ds.gba files. Change this if you do.
#all: $(TARGET).ds.gba
all: $(TARGET).nds


$(TARGET).ds.gba	: $(TARGET).nds

#---------------------------------------------------------------------------------
$(TARGET).nds	:	$(TARGET).arm7 $(TARGET).arm9
	@ndstool -c $(TARGET).nds -7 $(TARGET).arm7 -9 $(TARGET).arm9 # $(ICON) "$(TEXT1);$(TEXT2);$(TEXT3)"
#	@echo Copying $(TARGET).nds to web server...
#*** Change this path to whatever is appropriate on your system
#	@cp $(TARGET).nds /h/hp/libdevlight_example.nds

#---------------------------------------------------------------------------------
$(TARGET).arm7	: arm7/$(TARGET).elf
$(TARGET).arm9	: arm9/$(TARGET).elf

#---------------------------------------------------------------------------------
arm7/$(TARGET).elf:
	$(MAKE) -C arm7
	
#---------------------------------------------------------------------------------
arm9/$(TARGET).elf:
	$(MAKE) -C arm9

#---------------------------------------------------------------------------------
clean:
	$(MAKE) -C arm9 clean
	$(MAKE) -C arm7 clean
	rm -f $(TARGET).ds.gba $(TARGET).nds $(TARGET).arm7 $(TARGET).arm9
