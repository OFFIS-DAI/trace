import random
from abc import ABC, abstractmethod
from enum import Enum


class PacketSizeTrend(Enum):
    CONSTANT = 0
    DECREASING = 1
    INCREASING = 2


class DataSizeGenerator(ABC):

    def __init__(self,
                 packet_size_trend: PacketSizeTrend):
        self.packet_size_trend = packet_size_trend

    @abstractmethod
    def get_data_size(self):
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


class FixedDataSizeGenerator(DataSizeGenerator):
    def __init__(self,
                 data_size_byte: int):
        super().__init__(PacketSizeTrend.CONSTANT)
        self.packet_size_byte = data_size_byte

    def get_data_size(self):
        return self.packet_size_byte

    def get_description(self) -> str:
        return f'Fixed data size generator with data size = {self.packet_size_byte} B'


class IncreasingInIntervalDataSizeGenerator(DataSizeGenerator):
    def __init__(self,
                 lower_bound_byte: int,
                 upper_bound_byte: int):
        self.lower_bound_byte = lower_bound_byte
        self.upper_bound_byte = upper_bound_byte
        self.last_packet_size = lower_bound_byte
        super().__init__(PacketSizeTrend.INCREASING)

    def get_data_size(self):
        self.last_packet_size = random.randint(self.last_packet_size,
                                               int(self.last_packet_size +
                                                   (self.upper_bound_byte - self.last_packet_size) * 0.1))
        return self.last_packet_size

    def get_description(self) -> str:
        return (f'Increasing data size generator with lower bound = {self.lower_bound_byte} B,'
                f'upper bound = {self.upper_bound_byte} B')


class InIntervalDataSizeGenerator(DataSizeGenerator):
    def __init__(self,
                 lower_bound_byte: int,
                 upper_bound_byte: int):
        self.lower_bound_byte = lower_bound_byte
        self.upper_bound_byte = upper_bound_byte
        super().__init__(PacketSizeTrend.CONSTANT)

    def get_data_size(self):
        return random.randint(self.lower_bound_byte, self.upper_bound_byte)

    def get_description(self) -> str:
        return (f'In interval data size generator with lower bound = {self.lower_bound_byte} B,'
                f'upper bound = {self.upper_bound_byte} B')
