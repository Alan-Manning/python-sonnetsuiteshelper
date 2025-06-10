from abc import ABC, abstractmethod

# class Analyser(ABC):
#     """Analyser."""


class SingleResonatorAnalyser(ABC):
    """SingleResonatorAnalyser."""

    @abstractmethod
    def get_resonant_freq(self) -> float:
        pass

    @abstractmethod
    def get_Q_values(self) -> tuple[float, float, float]:
        pass

    @abstractmethod
    def get_three_dB_BW(self) -> float:
        pass
