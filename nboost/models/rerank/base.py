"""Base Class for ranking models"""

from typing import List
from nboost.models.base import BaseModel
from nboost import defaults


class RerankModel(BaseModel):
    def rank(self, query: str, choices: List[str],
             filter_results: type(defaults.filter_results) = defaults.filter_results) -> List[int]:
        """assign relative ranks to each choice"""

    def close(self):
        """Close the model"""
