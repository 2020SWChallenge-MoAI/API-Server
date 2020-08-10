import torch
import numpy as np
from transformers.data.processors import SquadExample, squad_convert_examples_to_features
from transformers import AutoTokenizer, AutoModelForQuestionAnswering


class KoELECTRA:
    def __init__(self, pretrained_model_path):
        # load fine-tuned model
        self.model = AutoModelForQuestionAnswering.from_pretrained(pretrained_model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_path)

        self.max_seq_length = 512
        self.doc_stride = 128
        self.max_query_length = 64
        self.max_answer_len = 32

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def get_answer(self, question, context, topk=1):
        assert self.model, "Model is not loaded"
        assert self.tokenizer, "Tokenizer is not loaded"

        example = SquadExample(None, question, context, None, None, None)

        features = squad_convert_examples_to_features(
            examples=[example],
            tokenizer=self.tokenizer,
            max_seq_length=self.max_seq_length,
            doc_stride=self.doc_stride,
            max_query_length=self.max_query_length,
            is_training=False,
            tqdm_enabled=False
        )

        model_input_names = self.tokenizer.model_input_names + ["input_ids"]
        fw_args = {k: [feature.__dict__[k] for feature in features] for k in model_input_names}

        with torch.no_grad():
            fw_args = {k: torch.tensor(v, device=self.device) for (k, v) in fw_args.items()}
            start, end = self.model(**fw_args)[:2]
            start, end = start.cpu().numpy(), end.cpu().numpy()

        min_null_score = 1000000
        answers = []
        for (feature, start_, end_) in zip(features, start, end):
            # question token, attention 아닌 부분 제외
            undesired_tokens = np.abs(np.array(feature.p_mask) - 1) & feature.attention_mask
            undesired_tokens_mask = undesired_tokens == 0.0

            # softmax시 영향 없도록 context아닌 부분은 -10000로 마스킹 
            start_ = np.where(undesired_tokens_mask, -10000.0, start_)
            end_ = np.where(undesired_tokens_mask, -10000.0, end_)

            # Normalize logits and spans to retrieve the answer
            start_ = np.exp(start_ - np.log(np.sum(np.exp(start_), axis=-1, keepdims=True)))
            end_ = np.exp(end_ - np.log(np.sum(np.exp(end_), axis=-1, keepdims=True)))

            min_null_score = min(min_null_score, (start_[0] * end_[0]).item())

            # Mask CLS
            start_[0] = end_[0] = 0.0

            starts, ends, scores = self.decode(start_, end_, topk, self.max_answer_len)
            char_to_word = np.array(example.char_to_word_offset)

            # Convert the answer (tokens) back to the original text
            answers += [
                {
                    "score": score.item(),
                    "start": np.where(char_to_word == feature.token_to_orig_map[s])[0][0].item(),
                    "end": np.where(char_to_word == feature.token_to_orig_map[e])[0][-1].item(),
                    "answer": " ".join(
                        example.doc_tokens[feature.token_to_orig_map[s]: feature.token_to_orig_map[e] + 1]
                    ),
                }
                for s, e, score in zip(starts, ends, scores)
            ]

        answers.append({"score": min_null_score, "start": 0, "end": 0, "answer": ""})
        answers = sorted(answers, key=lambda x: x["score"], reverse=True)[: topk]

        return answers

    def decode(self, start, end, topk, max_answer_len):
        """
        score 높은 start-end index topk개 반환
        """
        start, end = start[None], end[None]

        # Compute the score of each tuple(start, end) to be the real answer
        outer = np.matmul(np.expand_dims(start, -1), np.expand_dims(end, 1))

        # Remove candidate with end < start and end - start > max_answer_len
        candidates = np.tril(np.triu(outer), max_answer_len - 1)

        #  Inspired by Chen & al. (https://github.com/facebookresearch/DrQA)
        scores_flat = candidates.flatten()
        if topk == 1:
            idx_sort = [np.argmax(scores_flat)]
        elif len(scores_flat) < topk:
            idx_sort = np.argsort(-scores_flat)
        else:
            idx = np.argpartition(-scores_flat, topk)[0:topk]
            idx_sort = idx[np.argsort(-scores_flat[idx])]

        start, end = np.unravel_index(idx_sort, candidates.shape)[1:]
        return start, end, candidates[0, start, end]
