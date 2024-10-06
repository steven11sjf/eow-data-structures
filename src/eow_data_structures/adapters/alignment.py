from construct import Construct, evaluate, stream_read, stream_tell, stream_write


class AlignTo(Construct):
    def __init__(self, modulus=0x10, pattern=b"\x00"):
        super().__init__()
        self.modulus = modulus
        self.pattern = pattern
        self.flagbuildnone = True

    def _parse(self, stream, context, path):
        modulus = evaluate(self.modulus, context)
        position = stream_tell(stream, path)
        pad = modulus - (position % modulus)
        return stream_read(stream, pad, path)

    def _build(self, obj, stream, context, path):
        modulus = evaluate(self.modulus, context)
        position = stream_tell(stream, path)
        pad = modulus - (position % modulus)
        stream_write(stream, self.pattern * pad, pad, path)
