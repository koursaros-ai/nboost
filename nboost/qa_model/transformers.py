from transformers import *
import torch
import numpy as np


def _is_whitespace(c):
    if c == " " or c == "\t" or c == "\r" or c == "\n" or ord(c) == 0x202F:
        return True
    return False


class TransformersQAModel():

    def __init__(self, model='distilbert-base-uncased-distilled-squad',
                 max_query_length=64,
                 max_seq_length=512):
        self.model = DistilBertForQuestionAnswering.from_pretrained(model)
        self.tokenizer = DistilBertTokenizer.from_pretrained(model)
        self.max_query_length = max_query_length
        self.max_seq_length = max_seq_length

    def get_answer(self, question, context):
        doc_tokens = []
        char_to_word_offset = []
        prev_is_whitespace = True

        # Split on whitespace so that different tokens may be attributed to
        # their original position.
        for c in context:
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

        truncated_query = self.tokenizer.encode(question,
                                                add_special_tokens=False,
                                                max_length=self.max_query_length)

        encoded_dict = self.tokenizer.encode_plus(
            truncated_query,
            all_doc_tokens,
            max_length=self.max_seq_length,
            return_tensors='pt'
        )

        self.model.eval()
        with torch.no_grad():
            start_logits, end_logits = self.model(
                input_ids=encoded_dict['input_ids'])
            # add +2 for [CLS] and [SEP], and cut out last [SEP]
            start_logits = start_logits[0][len(truncated_query) + 2:-1]
            end_logits = end_logits[0][len(truncated_query) + 2:-1]

        assert len(end_logits) == len(tok_to_orig_index)
        start_tok = int(np.argmax(start_logits))
        end_tok = int(np.argmax(end_logits[start_tok + 1:])) + start_tok

        answer = ' '.join(doc_tokens[
                          tok_to_orig_index[start_tok]:tok_to_orig_index[
                                                           end_tok] + 1])
        # TODO: Add actual start / end and source passage id
        return answer, (start_tok, end_tok, 0)
