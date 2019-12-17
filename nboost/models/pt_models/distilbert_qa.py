from typing import Tuple
from transformers import DistilBertForQuestionAnswering, DistilBertTokenizer
import numpy as np
import torch
from nboost.models.qa import QAModel


def _is_whitespace(c):
    if c in " \t\r\n" or ord(c) == 0x202F:
        return True
    return False


class PtDistilBertQAModel(QAModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = DistilBertForQuestionAnswering.from_pretrained(self.model_dir)
        self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_dir)

    def get_answer(self, query: str, choice: str) -> Tuple[str, Tuple[int, int, int]]:
        """Return (answer, (candidate, start_pos, end_pos))"""
        doc_tokens = []
        char_to_word_offset = []
        prev_is_whitespace = True

        # Split on whitespace so that different tokens may be attributed to
        # their original position.
        for c in choice:
            if _is_whitespace(c):
                prev_is_whitespace = True
            else:
                if prev_is_whitespace:
                    doc_tokens.append(c)
                else:
                    doc_tokens[-1] += c
                prev_is_whitespace = False
            char_to_word_offset.append(len(doc_tokens) - 1)

        tok_to_orig_index = []
        all_doc_tokens = []
        for (i, token) in enumerate(doc_tokens):
            sub_tokens = self.tokenizer.tokenize(token)
            for sub_token in sub_tokens:
                tok_to_orig_index.append(i)
                all_doc_tokens.append(sub_token)

        truncated_query = self.tokenizer.encode(query,
                                                add_special_tokens=False,
                                                max_length=self.max_query_length)

        encoded_dict = self.tokenizer.encode_plus(
            truncated_query,
            all_doc_tokens,
            max_length=self.max_seq_len,
            return_tensors='pt'
        )

        self.model.eval()
        with torch.no_grad():
            start_logits, end_logits = self.model(
                input_ids=encoded_dict['input_ids'])
            # add +2 for [CLS] and [SEP], and cut out last [SEP]
            start_logits = start_logits[0][len(truncated_query) + 2:-1]
            end_logits = end_logits[0][len(truncated_query) + 2:-1]

        assert len(end_logits) == len(tok_to_orig_index) or len(end_logits) == \
               self.max_seq_len - len(truncated_query) - 3

        start_tok = int(np.argmax(start_logits))
        end_tok = int(np.argmax(end_logits[start_tok + 1:])) + start_tok

        answer = ' '.join(doc_tokens[
                          tok_to_orig_index[start_tok]:tok_to_orig_index[
                                                           end_tok] + 1])
        # TODO: Add actual start / end and source passage id
        return answer, (start_tok, end_tok, 0)
