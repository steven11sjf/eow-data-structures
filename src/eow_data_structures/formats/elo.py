from pathlib import Path

import construct
from construct.core import (
    Adapter,
    Array,
    Byte,
    Bytes,
    Check,
    Const,
    CString,
    Flag,
    Float32l,
    FocusedSeq,
    Int16ul,
    Int32ul,
    Pass,
    Struct,
    Switch,
    Tell,
)

from eow_data_structures.adapters.alignment import AlignTo


class Section(Adapter):
    def __init__(self, subcon, idx, endalignment: bool = True):
        super().__init__(
            FocusedSeq(
                "items",
                "position" / Tell,
                Check(lambda ctx: ctx._root.headers[idx].start == ctx.position),
                "items" / Array(lambda ctx: ctx._root.headers[idx].count, subcon),
                AlignTo() if endalignment else Pass,
            )
        )

    def _decode(self, obj, context, path):
        return obj

    def _encode(self, obj, context, path):
        return obj


class ELO(Adapter):
    subcon = construct.Debugger(
        Struct(
            Const(b"elo "),
            "version" / Const(0x01010001, Int32ul),
            "length" / Int32ul,
            "headers"
            / Array(
                32,
                Struct(
                    "count" / Int32ul,
                    "start" / Int32ul,
                ),
            ),
            Const(b"LVLE"),
            Const(11, Int32ul),
            Const(0, Int32ul),
            Const(0, Int32ul),
            Const(0, Int32ul),
            "actors"
            / Section(
                Struct(
                    "translation" / Float32l[3],
                    "unk2" / Int16ul,
                    "unk3" / Int16ul,
                    "unk4" / Float32l,
                    "unk5" / Float32l,
                    "tf" / Float32l,
                    "min_scale" / Float32l[3],
                    "max_scale" / Float32l[3],
                    "conditions" / Struct("key" / Int16ul, "value" / Int16ul)[4],
                    "actor_params" / Int16ul[8],
                    "unk6" / Int32ul,
                    "unk7" / Int16ul,
                    "unk8" / Byte[2],
                    "actor_name" / Int32ul,
                    "unk10" / Int16ul[12],
                    "unk11" / Byte[2],
                    "unk12" / Int16ul,
                ),
                0,
            ),
            "_empty" / Section(Pass, 1),
            "_unk2_hashes" / Section(Int32ul, 2),
            "_unk3" / Section(Int16ul, 3),
            "_unk4" / Section(Bytes(4)[6], 4),
            "_unk5" / Section(Bytes(4)[3], 5),
            "_unk6" / Section(Bytes(4), 6),
            "_unk7" / Section(Bytes(4)[12], 7),
            "_unk8" / Section(Bytes(4)[12], 8),
            "_unk9" / Section(Bytes(4), 9),
            "_unk10" / Section(Struct("unk1" / Int16ul[2], "unk2" / Int32ul), 10),
            "_unk11" / Section(Bytes(4), 11),
            "_unk12" / Section(Bytes(4)[12], 12),
            "_unk13" / Section(Bytes(4)[3], 13),
            "_unk14" / Section(Bytes(4)[12], 14),
            "_unk15" / Section(Bytes(4)[8], 15),
            "_unk16" / Section(Bytes(4)[2], 16),
            "_unk17" / Section(Int16ul, 17),
            "_unk18" / Section(Bytes(4)[2], 18),
            "_unk19" / Section(Bytes(4)[8], 19),
            "_unk20" / Section(Bytes(4)[2], 20),
            "_unk21" / Section(Bytes(4), 21),
            "_unk22" / Section(Float32l[2], 22),
            "_empty23" / Section(Pass, 23),
            "_unk24" / Section(Float32l[4], 24),
            "_unk25" / Section(Float32l[4], 25, endalignment=False),
            "actorParams"
            / Section(
                Struct(
                    "type" / Int32ul,
                    "value"
                    / Switch(
                        construct.this.type,
                        {
                            0: Const(0, Int32ul),
                            1: FocusedSeq("b", "b" / Flag, Const(b"\x00\x00\x00")),
                            2: Int32ul,
                            3: Float32l,
                            4: Int32ul,
                        },
                    ),
                ),
                26,
                endalignment=False,
            ),
            "_unk27" / Section(Bytes(4), 27, endalignment=False),
            "_empty28" / Section(Pass, 28, endalignment=False),
            "_unk29" / Section(Int16ul, 29, endalignment=False),
            "_stringOffsets" / Section(Int32ul, 30),
            "strings" / Section(CString("ascii"), 31),
            construct.Terminated,
        )
    )

    def __init__(self):
        super().__init__(self.subcon)

    def _decode(self, obj, context, path):
        for param in obj.actorParams:
            if param.type == 4:
                param.value = obj.strings[param.value]

        for actor in obj.actors:
            actor.actor_params = construct.ListContainer([obj.actorParams[ap] for ap in actor.actor_params])
            actor.conditions = construct.ListContainer(
                [construct.Container(key=obj.actorParams[c.key], value=c.value) for c in actor.conditions]
            )

        return obj

    def _encode(self, obj, context, path):
        for actor in obj.actors:
            actor.actor_params = construct.ListContainer([obj.actorParams.index(ap) for ap in actor.actor_params])
            actor.conditions = construct.ListContainer(
                [construct.Container(key=obj.actorParams.index(c.key), value=c.value) for c in actor.conditions]
            )

        for param in obj.actorParams:
            if param.type == 4:
                param.value = obj.strings.index(param.value)
        return obj


file = Path("d:/echoes100/region_common/level/S_Dungeon046.elo").read_bytes()
parsed = ELO().parse(file)
rebuilt = ELO().build(parsed)
if rebuilt == file:
    print("Matching!")
# Path("a:/rebuilt.elo").write_bytes(rebuilt)
