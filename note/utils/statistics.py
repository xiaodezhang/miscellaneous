from enum import Enum, auto

from loguru import logger
from appconfig import app_config
from patient.calibration import Calibration

class Part(Enum):
    LEFT = auto()
    LEFT_HEEL = auto()
    LEFT_METATARSAL = auto()
    RIGHT = auto()
    RIGHT_HEEL = auto()
    RIGHT_METATARSAL = auto()

class Statistics:
    # 计算饱和度
    def __init__(self, net):
        self._net = net

    def part_to_feet(self, part: Part) -> list[list[int]]:
        return {
            Part.LEFT: self._net.left
            , Part.LEFT_HEEL: self._net.left_heel
            , Part.LEFT_METATARSAL: self._net.left_metatarsal
            , Part.RIGHT: self._net.right
            , Part.RIGHT_HEEL: self._net.right_heel
            , Part.RIGHT_METATARSAL: self._net.right_metatarsal
        }[part]

    def calculate_saturation(self, data: list[int], part: Part):
        feet = self.part_to_feet(part)
        # TODO: 多个极值平均
        max_data = max([data[p[2]] for p in feet])
        return round(max_data/(2**app_config.bits), 1)

    # 计算区域和
    def area_sum(self, data: list[float]|list[int], part: Part):
        feet = self.part_to_feet(part)
        return round(sum([data[p[2]] for p in feet]), 2)

    def _gross(self, data, calibration, side):
        if calibration.gross:
            gross_data = []
            match side:
                case 'all':
                    gross_data = calibration.gross
                case 'left':
                    gross_data = calibration.gross[:64]
                case 'right':
                    gross_data = calibration.gross[64:]
            assert len(data)==len(gross_data)
            count = len(data)
            trans_data = []
            for i in range(count):
                d = data[i]-gross_data[i]
                if d < 0:
                    d = 0
                trans_data.append(d)
            return trans_data
        return data

    # 标定数据
    def calibrate(self, data, calibration: Calibration, side) -> list[float]:
        assert data
        trans_data = self._gross(data, calibration, side)
        match side:
            case 'all':
                for p in self._net.left:
                    trans_data[p[2]] = trans_data[p[2]]*calibration.left
                for p in self._net.right:
                    trans_data[p[2]] = trans_data[p[2]]*calibration.right
            case 'left':
                for p in self._net.left:
                    trans_data[p[2]] = trans_data[p[2]]*calibration.left
            case 'right':
                for p in self._net.right:
                    trans_data[p[2]] = trans_data[p[2]]*calibration.right
        return trans_data
