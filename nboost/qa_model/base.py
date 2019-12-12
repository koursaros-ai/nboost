from typing import Tuple, List

class QAModel:
  """Base class for QA Models"""

  def __init__(self):
    super().__init__()

  def get_answer(self, question: str, context: str) -> Tuple[str, Tuple[int, int, int]]:
    """Return (answer, (candidate, start_pos, end_pos))"""
    raise NotImplementedError()