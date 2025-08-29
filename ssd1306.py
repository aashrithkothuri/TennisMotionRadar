# Minimal MicroPython SSD1306 driver (I2C/SPI)
from micropython import const
import framebuf

# Commands
SET_CONTRAST     = const(0x81)
SET_ENTIRE_ON    = const(0xA4)
SET_NORM_INV     = const(0xA6)
SET_DISP         = const(0xAE)
SET_MEM_ADDR     = const(0x20)
SET_COL_ADDR     = const(0x21)
SET_PAGE_ADDR    = const(0x22)
SET_DISP_START_LINE = const(0x40)
SET_SEG_REMAP    = const(0xA0)
SET_MUX_RATIO    = const(0xA8)
SET_COM_OUT_DIR  = const(0xC0)
SET_DISP_OFFSET  = const(0xD3)
SET_COM_PIN_CFG  = const(0xDA)
SET_DISP_CLK_DIV = const(0xD5)
SET_PRECHARGE    = const(0xD9)
SET_VCOM_DESEL   = const(0xDB)
SET_CHARGE_PUMP  = const(0x8D)

class SSD1306:
    def __init__(self, width, height, external_vcc=False):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc
        self.pages = self.height // 8
        self.buffer = bytearray(self.pages * self.width)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self._init_display()

    # Drawing helpers (proxied to FrameBuffer)
    def fill(self, c): self.fb.fill(c)
    def pixel(self, x, y, c): self.fb.pixel(x, y, c)
    def hline(self, x, y, w, c): self.fb.hline(x, y, w, c)
    def vline(self, x, y, h, c): self.fb.vline(x, y, h, c)
    def line(self, x1, y1, x2, y2, c): self.fb.line(x1, y1, x2, y2, c)
    def rect(self, x, y, w, h, c): self.fb.rect(x, y, w, h, c)
    def fill_rect(self, x, y, w, h, c): self.fb.fill_rect(x, y, w, h, c)
    def text(self, s, x, y, c=1): self.fb.text(s, x, y, c)
    def blit(self, fbuf, x, y): self.fb.blit(fbuf, x, y)

    def poweroff(self): self._cmd(SET_DISP | 0x00)
    def poweron(self):  self._cmd(SET_DISP | 0x01)
    def contrast(self, val): self._cmd(SET_CONTRAST); self._cmd(val & 0xFF)
    def invert(self, inv): self._cmd(SET_NORM_INV | (1 if inv else 0))

    def rotate(self, rotated):
        self._cmd((SET_COM_OUT_DIR | (0x08 if rotated else 0x00)))
        self._cmd((SET_SEG_REMAP | (0x01 if rotated else 0x00)))

    # Additional helper for drawing scaled text 
    def draw_text_scaled(self, text, x, y, scale, color=1):

        # Width and height in pixels (each char takes 8x8)
        w, h = 8*len(text), 8

        # Off screen buffer with text
        scratch = bytearray((w*h)//8) # Contains just the rigth amount of bytes
        fb = framebuf.FrameBuffer(scratch, w, h, framebuf.MONO_VLSB)
        fb.text(text, 0, 0, 1)

        # Looping through each pixel
        for yy in range(h):
            for xx in range(w):

                # If pixel is "on", draw a scalexscale rectangle representing one pixel
                if fb.pixel(xx, yy):
                    self.fill_rect(x + xx*scale, y + yy*scale, scale, scale, color)

    # Additional helper to scale text such that it is as large as possible but still fits in oled
    def draw_text_max(self, text):

        # Width and height in pixels (each char takes 8x8)
        w, h = 8*len(text), 8

        # How much scale needed to fit width and height within constraints
        w_scale = self.width//w
        h_scale = self.height//h

        # Going with lower value (so that everything fits)
        scale = min(w_scale,h_scale)

        # Drawing scaled text
        self.draw_text_scaled(text, 0, 0, scale)

    def _init_display(self):
        for c in (
            SET_DISP | 0x00,
            SET_MEM_ADDR, 0x00,                # horizontal addr mode
            SET_DISP_START_LINE | 0x00,
            SET_SEG_REMAP | 0x01,
            SET_MUX_RATIO, self.height - 1,
            SET_COM_OUT_DIR | 0x08,
            SET_DISP_OFFSET, 0x00,
            SET_COM_PIN_CFG, 0x02 if self.height == 32 else 0x12,
            SET_DISP_CLK_DIV, 0x80,
            SET_PRECHARGE,   0x22 if self.external_vcc else 0xF1,
            SET_VCOM_DESEL,  0x30,
            SET_CONTRAST,    0xFF,
            SET_ENTIRE_ON,
            SET_NORM_INV,
            SET_CHARGE_PUMP, 0x10 if self.external_vcc else 0x14,
            SET_DISP | 0x01
        ):
            self._cmd(c)
        self.fill(0)
        self.show()

    def show(self):
        for page in range(self.pages):
            self._cmd(SET_PAGE_ADDR); self._cmd(page); self._cmd(self.pages - 1)
            self._cmd(SET_COL_ADDR);  self._cmd(0);    self._cmd(self.width - 1)
            # send one page (width bytes) in small chunks for I2C reliability
            start = page * self.width
            end = start + self.width
            buf = self.buffer[start:end]
            self._data_chunks(buf)

    # Low-level hooks (implemented in subclasses)
    def _cmd(self, cmd): raise NotImplementedError
    def _data_chunks(self, buf): raise NotImplementedError

class SSD1306_I2C(SSD1306):
    def __init__(self, width, height, i2c, addr=0x3C, external_vcc=False):
        self.i2c = i2c
        self.addr = addr
        self._tmp = bytearray(2)   # command buffer
        super().__init__(width, height, external_vcc)

    def _cmd(self, cmd):
        self._tmp[0] = 0x80  # Co=1 D/C#=0
        self._tmp[1] = cmd & 0xFF
        self.i2c.writeto(self.addr, self._tmp)

    def _data_chunks(self, buf, chunk=16):
        # D/C#=1 data prefix 0x40
        for i in range(0, len(buf), chunk):
            self.i2c.writeto(self.addr, b'\x40' + buf[i:i+chunk])

class SSD1306_SPI(SSD1306):
    def __init__(self, width, height, spi, dc, res, cs, external_vcc=False):
        self.spi, self.dc, self.res, self.cs = spi, dc, res, cs
        self.dc.init(self.dc.OUT, value=0)
        self.res.init(self.res.OUT, value=0)
        self.cs.init(self.cs.OUT,  value=1)
        # reset
        self.res(1); self.res(0); self.res(1)
        super().__init__(width, height, external_vcc)

    def _cmd(self, cmd):
        self.cs(1); self.dc(0); self.cs(0)
        self.spi.write(bytearray([cmd & 0xFF]))
        self.cs(1)

    def _data_chunks(self, buf, chunk=32):
        self.cs(1); self.dc(1); self.cs(0)
        for i in range(0, len(buf), chunk):
            self.spi.write(buf[i:i+chunk])
        self.cs(1)
